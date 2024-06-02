pipeline {
    agent any

    stages {
        stage('Backup') {
            steps {
                script {
                    if (fileExists('backup_database.py')) {
                        sh 'start /B python3 backup_database.py'
                    } else {
                        echo 'Файл backup_database.py не найден'
                    }
                }
            }
        }
    }
}