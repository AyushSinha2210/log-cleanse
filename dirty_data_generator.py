# dirty_data_generator.py
import random
import csv

def generate_dirty_data(filename: str = "dirty_auth_logs.csv", rows: int = 10000) -> None:
    headers = ["timestamp", "user_id", "ip_address", "request_path", "response_time_ms", "status_code"]
    
    benign_paths = ["/api/v1/login", "/dashboard", "/api/v1/profile", "/checkout", "/health"]
    malicious_paths = [
        "/api/v1/users?id=1' OR '1'='1",
        "/search?q=<script>alert('pwned')</script>",
        "/api/v1/auth?token=bearer a93b827df10283c71629471bbad09e812f",
        "/admin' UNION SELECT * FROM users--"
    ]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for i in range(1, rows + 1):
            # 5% chance of corrupt row formatting
            if random.random() < 0.05:
                writer.writerow(["CORRUPTED", "NULL", "invalid_ip", "", "-50.0", "NOT_A_CODE"])
                continue

            timestamp = f"2026-10-20T08:{random.randint(10,59)}:{random.randint(10,59)}Z"
            user_id = random.choice([i, -99, ""]) if random.random() < 0.02 else i
            
            # 3% chance of bad IP
            ip = "999.888.777.666" if random.random() < 0.03 else f"192.168.1.{random.randint(1, 254)}"
            
            # 4% chance of security payload
            path = random.choice(malicious_paths) if random.random() < 0.04 else random.choice(benign_paths)
            
            # Response times with realistic long tail + outliers
            resp_time = -12.0 if random.random() < 0.02 else round(random.expovariate(1/150) + 10, 2)
            status = random.choice([200, 200, 200, 401, 403, 500])

            writer.writerow([timestamp, user_id, ip, path, resp_time, status])

    print(f"[+] Generated {rows} dirty log rows in '{filename}'.")

if __name__ == "__main__":
    generate_dirty_data()