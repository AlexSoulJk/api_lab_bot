pipeline {
    agent any

    stages {
        stage('Backup') {
            steps {
                script {
                    sh 'py backup_database.py'
                }
            }
        }
    }
}