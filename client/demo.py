# client/demo.py

from client import A2AClient


def main():
    with A2AClient("http://localhost:8000") as client:
        # 1. Fetch and display Agent Card info
        card = client.fetch_agent_card()
        print(f"Agent name : {card['name']}")
        print(f"Agent ID   : {card['id']}")
        print(f"Version    : {card['version']}")

        # 2. Display skills
        skills = client.get_skills()
        print(f"\nSkills ({len(skills)}):")
        for skill in skills:
            print(f"  - [{skill['id']}] {skill['name']}: {skill['description']}")

        # 3. Send a task and print the echoed response
        print("\nSending task: 'Hello from the client!'")
        response = client.send_task("Hello from the client!")
        result = client.extract_text(response)
        print(f"Response   : {result}")

        # 4. Test !summarise skill
        print("\nSending task: '!summarise The A2A protocol enables agent communication.'")
        response2 = client.send_task("!summarise The A2A protocol enables agent communication.")
        result2 = client.extract_text(response2)
        print(f"Response   : {result2}")


if __name__ == "__main__":
    main()