pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('dockerhub-creds')
        BEST_ACC = credentials('best-accuracy')
    }

    stages {

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                . venv/bin/activate
                python scripts/train.py
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                script {
                    ACC = sh(script: "jq '.accuracy' app/artifacts/metrics.json", returnStdout: true).trim()
                    env.CURR_ACC = ACC
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                script {
                    if (env.CURR_ACC.toFloat() > BEST_ACC.toFloat()) {
                        env.BUILD_IMAGE = "true"
                    } else {
                        env.BUILD_IMAGE = "false"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when { expression { env.BUILD_IMAGE == "true" } }
            steps {
                sh '''
                docker login -u $DOCKER_CREDS_USR -p $DOCKER_CREDS_PSW
                docker build -t $DOCKER_CREDS_USR/wine:${BUILD_NUMBER} .
                docker tag $DOCKER_CREDS_USR/wine:${BUILD_NUMBER} $DOCKER_CREDS_USR/wine:latest
                '''
            }
        }

        stage('Push Docker Image') {
            when { expression { env.BUILD_IMAGE == "true" } }
            steps {
                sh '''
                docker push $DOCKER_CREDS_USR/wine:${BUILD_NUMBER}
                docker push $DOCKER_CREDS_USR/wine:latest
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**'
        }
    }
}