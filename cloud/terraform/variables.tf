variable "aws_region" {
  description = "The AWS region to deploy in"
  type        = string
  default     = "eu-west-3"
}

variable "ami_id" {
  description = "The AMI ID to use for the instance"
  type        = string
  default     = "ami-00ac45f3035ff009e"
}

variable "instance_type" {
  description = "The instance type to use"
  type        = string
  default     = "t3a.medium"
}
