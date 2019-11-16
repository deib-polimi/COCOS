import argparse
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from flask_cors import CORS
from controller_manager import ControllerManager

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(controller.get_logs())


def control():
    app.logger.info("Controller updating...")
    controller.update()
    app.logger.info("Controller updated, waiting for next clock...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--containers_manager', type=str, required=True)
    parser.add_argument('--requests_store', type=str, required=True)
    parser.add_argument('--min_c', type=float, required=True)
    parser.add_argument('--max_c', type=float, required=True)
    parser.add_argument('--time', type=float, required=True)
    parser.add_argument('--actuator_port', type=int, default=5000)
    args = parser.parse_args()

    # init log
    format = "%(threadName)s:%(asctime)s: %(message)s"
    logging.basicConfig(format=format,
                        level=logging.INFO,
                        datefmt="%H:%M:%S")

    models_endpoint = args.containers_manager + "/models"
    logging.info("Setting models manager to: %s", models_endpoint)
    containers_endpoint = args.containers_manager + "/containers"
    logging.info("Setting containers_manager to: %s", containers_endpoint)
    requests_endpoint = args.requests_store
    logging.info("Setting requests_store to: %s", requests_endpoint)

    status = "init controller"
    logging.info(status)
    controller = ControllerManager(models_endpoint,
                                   containers_endpoint,
                                   requests_endpoint,
                                   args.actuator_port,
                                   args.time,
                                   args.min_c,
                                   args.max_c)
    controller.init()

    sched = BackgroundScheduler()
    sched.add_job(control, 'interval', seconds=args.time)
    sched.start()

    status = "running"
    logging.info(status)
    app.run(host='0.0.0.0', port=5003, debug=False)
