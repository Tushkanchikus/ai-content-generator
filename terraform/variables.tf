variable "folder_id" {
  type        = string
  description = "ID каталога Yandex Cloud"
}

variable "api_key" {
  type        = string
  description = "API-ключ для YandexGPT"
  sensitive   = true
}

variable "bucket_name" {
  type        = string
  description = "Имя бакета для сайта"
  default     = "my-ai-content-bucket-12345"
}
