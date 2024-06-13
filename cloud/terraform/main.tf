provider "aws" {
  region = var.aws_region
}

resource "aws_key_pair" "deployer" {
  key_name   = "testing-key"
  public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEwiM3yyAlCZN2RwYqbYcimGwwCH/H1FvTq+TrmKy1S+ emmanuel.orozco@adeo.com"
}


resource "aws_security_group" "flask_server_sg" {
  name        = "flask_server_sg"
  description = "Allow SSH and HTTP traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "flask_server" {
  ami           = var.ami_id
  instance_type = var.instance_type

  key_name      = aws_key_pair.deployer.key_name

  tags = {
    Name = "FlaskServerInstance"
  }

  # Security group to allow SSH and HTTP access
  vpc_security_group_ids = [aws_security_group.flask_server_sg.id]
}