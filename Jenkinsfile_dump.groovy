pipeline {
    agent any

    stages {
        stage('Backup') {
            steps {
                script {
                    sh 'python3 dump_database.py'
                }
            }
        }
    }
}