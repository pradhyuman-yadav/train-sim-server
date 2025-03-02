pipeline {
    agent any

    environment {
        TRAINSIM_SUPABASE_URL = credentials('TRAINSIM_SUPABASE_URL')
        TRAINSIM_SUPABASE_KEY = credentials('TRAINSIM_SUPABASE_KEY')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/pradhyuman-yadav/train-sim-server.git' // Your repo URL
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Tag the image with the commit SHA
                    env.IMAGE_TAG = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    sh """
                    docker build \\
                    --build-arg TRAINSIM_SUPABASE_URL="${TRAINSIM_SUPABASE_URL}" \\
                    --build-arg TRAINSIM_SUPABASE_KEY="${TRAINSIM_SUPABASE_KEY}" \\
                    -t train-sim-server:latest .
                    """
                    // Optionally, tag with 'latest' as well
//                     sh "docker tag train-sim-server:latest"
                }
            }
        }

//         stage('Push to Registry') { // Optional, but recommended
//             when {
//               expression {
//                 // Only run this stage if DOCKER_IMAGE_NAME is set, indicating a registry is used
//                 return env.DOCKER_IMAGE_NAME != null && env.DOCKER_IMAGE_NAME != ""
//               }
//             }
//             steps {
//                 script {
//                   withDockerRegistry([credentialsId: 'your-docker-registry-credentials', url: "https://index.docker.io/v1/"]) { //replace this if you are not using docker hub
//                     sh "docker push ${DOCKER_IMAGE_NAME}:${env.IMAGE_TAG}"
//                     sh "docker push ${DOCKER_IMAGE_NAME}:latest"
//                   }
//
//                 }
//             }
//         }
        stage('Run Docker Container') {
            steps {
                script {
                    // Stop/remove any old container (with proper error handling)
                    try {
                        sh 'docker rm -f train-sim-server'
                    } catch (Exception e) {
                        echo "Container 'train-sim-server' did not exist or could not be removed. Continuing..."
                        // Optionally, log the full exception:  echo e.getMessage()
                    }

                    // Run the new container, using --env-file for runtime secrets
                    sh """
                    docker run --network host -v /proc:/host_proc -e HOST_PROC=/host_proc -d \\
                        --name train-sim-server \\
                        -p 8000:8000 \\
                        -e TRAINSIM_SUPABASE_URL="${TRAINSIM_SUPABASE_URL}" \\
                        -e TRAINSIM_SUPABASE_KEY="${TRAINSIM_SUPABASE_KEY}" \\
                        train-sim-server:latest
                    """
                }
            }
        }

        stage('Cleanup') { // Optional
            steps {
                sh "ssh -o StrictHostKeyChecking=no $SSH_AGENT_USR@${HOME_SERVER_IP} 'docker image prune -a --volumes'" // Remove dangling images
            }
        }
    }
}
