pipeline {
    agent any

    environment {
        IMAGE_NAME = "2022bcs0229swapna/wine_predict_2022bcs0229:latest"
        CONTAINER_NAME = "wine_test_container"
    }

    stages {

        stage('Pull Image') {
            steps {
                sh 'docker pull $IMAGE_NAME'
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                docker rm -f $CONTAINER_NAME || true
                docker run -d -p 8000:8000 \
                --add-host=host.docker.internal:host-gateway \
                --name $CONTAINER_NAME $IMAGE_NAME
                '''
            }
        }

        stage('Wait for Service Readiness') {
            steps {
                script {
                    timeout(time: 60, unit: 'SECONDS') {
                        waitUntil {
                            def response = sh(
                                script: "curl -s -o /dev/null -w '%{http_code}' http://host.docker.internal:8000/health || true",
                                returnStdout: true
                            ).trim()
                            return (response == "200")
                        }
                    }
                }
            }
        }

        stage('Valid Inference Test') {
            steps {
                script {
                    sh '''
                    echo "Sending Valid Inference Request..."
                    curl -X POST http://host.docker.internal:8000/predict \
                    -H "Content-Type: application/json" \
                    -d '{
                        "fixed_acidity":7.4,
                        "volatile_acidity":0.7,
                        "citric_acid":0.0,
                        "residual_sugar":1.9,
                        "chlorides":0.076,
                        "free_sulfur_dioxide":11.0,
                        "total_sulfur_dioxide":34.0,
                        "density":0.9978,
                        "pH":3.51,
                        "sulphates":0.56,
                        "alcohol":9.4
                    }'
                    '''
                    
                    def response = sh(
                        script: """curl -s -X POST http://host.docker.internal:8000/predict \
                        -H "Content-Type: application/json" \
                        -d '{
                            "fixed_acidity":7.4,
                            "volatile_acidity":0.7,
                            "citric_acid":0.0,
                            "residual_sugar":1.9,
                            "chlorides":0.076,
                            "free_sulfur_dioxide":11.0,
                            "total_sulfur_dioxide":34.0,
                            "density":0.9978,
                            "pH":3.51,
                            "sulphates":0.56,
                            "alcohol":9.4
                        }'""",
                        returnStdout: true
                    ).trim()

                    echo "Valid Response: ${response}"

                    if (!(response.contains("wine_quality"))) {
                        error("Prediction field missing")
                    }
                }
            }
        }

        stage('Invalid Inference Test') {
            steps {
                script {
                    def response = sh(
                        script: """curl -s -o /dev/null -w '%{http_code}' -X POST http://host.docker.internal:8000/predict \
                        -H 'Content-Type: application/json' \
                        -d '{"fixed_acidity":7.4}'""",
                        returnStdout: true
                    ).trim()

                    echo "Invalid Status Code: ${response}"

                    if (response != "422") {
                        error("Invalid input did not return expected error")
                    }
                }
            }
        }

        stage('Stop Container') {
            steps {
                sh '''
                docker stop $CONTAINER_NAME || true
                docker rm $CONTAINER_NAME || true
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline PASSED"
        }
        failure {
            echo "Pipeline FAILED"
        }
        always {
            sh 'docker rm -f $CONTAINER_NAME || true'
        }
    }
}