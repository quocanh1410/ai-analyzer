import requests
import sys

# Loki API
url = "http://localhost:3100/loki/api/v1/query_range"

# Chỉ lấy log lỗi hữu ích, bỏ monitoring để tránh nhiễu
query = {
    "query": '''
{job=~".+", namespace!="monitoring"}
|~ "(?i)bad address|error|failed|exception|refused|timeout|panic|crash"
''',
    "limit": 20,
    "direction": "backward"
}

try:

    r = requests.get(
        url,
        params=query,
        timeout=10
    )

except Exception as e:

    print("Cannot connect to Loki:")
    print(e)
    sys.exit()


# kiểm tra lỗi HTTP
if r.status_code != 200:

    print("Loki error:")
    print(r.status_code)
    print(r.text)

    sys.exit()


# kiểm tra JSON
try:

    data = r.json()

except Exception:

    print("Invalid Loki response:")
    print(r.text)

    sys.exit()


all_logs=[]
seen=set()

results=data.get("data",{}).get("result",[])

if not results:

    print("No matching logs found")
    sys.exit()


for stream in results:

    labels=stream["stream"]

    job=labels.get("job","unknown")
    pod=labels.get("pod","unknown")
    namespace=labels.get("namespace","unknown")
    container=labels.get("container","unknown")

    for value in stream["values"]:

        timestamp,log=value

        line=(
            f"[Namespace:{namespace}] "
            f"[Pod:{pod}] "
            f"[Container:{container}] "
            f"{log}"
        )

        # tránh log trùng
        if line not in seen:
            seen.add(line)
            all_logs.append(line)


# giới hạn log gửi AI
logs_text="\n".join(all_logs[:10])

print("\n===== LOGS SENT TO AI =====\n")
print(logs_text)


# gửi sang AI
try:

    response=requests.post(
        "http://localhost:8000/analyze",
        json={
            "logs":logs_text
        },
    )

except Exception as e:

    print("\nCannot connect to AI service:")
    print(e)

    sys.exit()


if response.status_code!=200:

    print("\nAI service error:")
    print(response.text)

    sys.exit()


print("\n===== AI ANALYSIS =====\n")

print(response.json()["analysis"])