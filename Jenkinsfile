node
{
   stage('Test') 
   {
       sh "pip3 install -r requirements.txt"
       sh "pip3 install -e ."
       sh "pytest --pyargs -s tests;"
   }    
}