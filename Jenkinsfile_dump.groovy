pipeline {
    agent any

    stages {
        stage('Backup') {
            steps {
                script {
                    if (fileExists('backup_database.py')) {
                        sh 'py backup_database.py'
                    } else {
                        echo 'Файл backup_database.py не найден'
                    }
                }
            }
        }
    }
}