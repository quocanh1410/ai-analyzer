import subprocess
import json
import time
import requests

# =========================
# AI SERVICE
# =========================

AI_URL = "http://localhost:8000/analyze"

# =========================
# EVENT FILTER
# =========================

ERROR_REASONS = [
    "Failed",
    "BackOff",
    "Unhealthy",
    "FailedScheduling",
    "ImagePullBackOff",
    "CrashLoopBackOff",
    "OOMKilled",
    "ErrImagePull"
]

print("🚀 Kubernetes Event Collector Started...")

seen = set()

while True:

    try:

        raw = subprocess.check_output(
            [
                "kubectl",
                "get",
                "events",
                "-A",
                "-o",
                "json"
            ]
        )

        data = json.loads(raw)

        items = data.get("items", [])

        for item in items:

            reason = item.get("reason", "")
            message = item.get("message", "")

            namespace = item.get(
                "metadata",
                {}
            ).get(
                "namespace",
                "unknown"
            )

            involved = item.get(
                "involvedObject",
                {}
            )

            kind = involved.get(
                "kind",
                ""
            )

            name = involved.get(
                "name",
                ""
            )

            # lọc event lỗi
            matched = any(
                x.lower() in reason.lower()
                for x in ERROR_REASONS
            )

            if matched:

                line = (
                    f"[Namespace:{namespace}] "
                    f"[{kind}:{name}] "
                    f"[Reason:{reason}] "
                    f"{message}"
                )

                # tránh duplicate
                if line not in seen:

                    seen.add(line)

                    print("\n🚨 K8S EVENT ALERT\n")
                    print(line)

                    # =========================
                    # SEND TO AI
                    # =========================

                    try:

                        response = requests.post(
                            AI_URL,
                            json={
                                "logs": line
                            },
                            #timeout=60
                        )

                        if response.status_code == 200:

                            print(
                                "\n===== AI ANALYSIS =====\n"
                            )

                            print(
                                response.json()["analysis"]
                            )

                        else:

                            print("\nAI service error:")
                            print(response.text)

                    except Exception as e:

                        print("\nCannot connect to AI:")
                        print(e)

    except Exception as e:

        print("\nCollector error:")
        print(e)

    time.sleep(10)