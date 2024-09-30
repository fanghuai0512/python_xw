import requests

url = "http://121.37.97.10:9000/collectTask/getUserCollectTask"
headers = {
    "accept": "*/*",
    "Authorization": "974591bc2cbe41ca85ecc784ec09d341"
}
data = ""

response = requests.post(url, headers=headers, data=data)

print(response.status_code)  # 打印响应状态码
print(response.json())