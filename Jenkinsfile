pipeline {
    agent any
    environment {
        ansible_server_private_ip = credentials('ansible_server_private_ip')
        kubernetes_server_private_ip = credentials('kubernetes_server_private_ip')
    }
    
    stages {
        stage('gitclone') {
            steps {
                script {
                    git url: "https://github.com/Gerardbulky/devops.git", branch: "main"
                    echo "Workspace Path: ${WORKSPACE}/deployment.yaml"
                }
            }
        }
        stage('Sending Dockerfile to Ansible server'){
            steps {
                script {
                    sshagent(['ansible-server']) {
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip}"
                        sh "scp -r /var/lib/jenkins/workspace/vault-app/* ubuntu@${ansible_server_private_ip}:/home/ubuntu"
                    }
                }
            }
        }
        stage('Docker build image'){
            steps {
                script {
                    sshagent(['ansible-server']) {
                     //building docker image starts
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} cd /home/ubuntu/"
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} docker image build -t cicd-demos:v-$BUILD_ID ."
                     //building docker image ends
                     //Tagging docker image starts
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} docker image tag cicd-demos:v-$BUILD_ID bossmanjerry/cicd-demos:v-$BUILD_ID"
                     sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} docker image tag cicd-demos:v-$BUILD_ID bossmanjerry/cicd-demos:latest"
                     //Tagging docker image ends
                    }
                }
            }
        }
        stage('Push images to dockerhub') {
            steps {
                script {
                    sshagent(['ansible-server']) {
                    // Logging into vault
                        withVault(
                            configuration: [
                                disableChildPoliciesOverride: false, 
                                timeout: 60, 
                                vaultCredentialId: 'vault-jenkins-role', 
                                vaultUrl: 'http://51.21.129.213:8200'], 
                                vaultSecrets: [
                                    [path: 'secrets/creds/my-secret-text', secretValues: [[vaultKey: 'dockerhub_username'], [vaultKey: 'dockerhub_password']]]]) {
                            sh 'echo $dockerhub_password | ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} docker login -u $dockerhub_username --password-stdin'
                            sh 'ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} docker image push bossmanjerry/cicd-demos:v-$BUILD_ID'
                            sh 'ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} docker image push bossmanjerry/cicd-demos:latest'
                            //also delete old docker images
                            sh 'ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} docker image rm bossmanjerry/cicd-demos:v-$BUILD_ID bossmanjerry/cicd-demos:latest cicd-demos:v-$BUILD_ID'
                        }
                        
                    }
                }
            }
        }
        stage('Copy files from jenkins to kubernetes server'){
            steps {
                script {
                    sshagent(['kubernetes-server']) {
                        sh 'ssh -o StrictHostKeyChecking=no ubuntu@${kubernetes_server_private_ip} cd /home/ubuntu/'
                        sh 'scp -r /var/lib/jenkins/workspace/vault-app/* ubuntu@${kubernetes_server_private_ip}:/home/ubuntu'
                    }
                }
            }
        }
        stage('Kubernetes deployment using ansible'){
            steps {
                script {
            
                    sshagent(['ansible-server']) {
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} cd /home/ubuntu/"
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} ansible -m ping ${kubernetes_server_private_ip}"
                        sh "ssh -o StrictHostKeyChecking=no ubuntu@${ansible_server_private_ip} ansible-playbook ansible-playbook.yml"
                    } 
                }
            }
        }
        
    }
}
