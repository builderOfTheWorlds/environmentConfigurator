#!/usr/bin/env python3
"""
Conversation History Analyzer for Gemini CLI
Analyzes ~/.gemini/history.jsonl to extract patterns, preferences, and recommendations
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Any

class ConversationAnalyzer:
    def __init__(self, history_file: str = "~/.gemini/history.jsonl"):
        self.history_file = Path(history_file).expanduser()
        self.conversations = []
        self.stats = defaultdict(int)

    def load_conversations(self) -> List[Dict[str, Any]]:
        """Load all conversations from JSONL file"""
        conversations = []
        if not self.history_file.exists():
            return conversations
        with open(self.history_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    conversations.append(json.loads(line))
        return conversations

    def analyze_task_frequency(self, conversations: List[Dict]) -> Dict[str, int]:
        """Analyze frequency of different task types"""
        keywords = {
            'git': ['git', 'commit', 'branch', 'push', 'pull', 'merge'],
            'file_ops': ['create', 'modify', 'delete', 'move', 'file'],
            'debug': ['error', 'bug', 'debug', 'fix', 'not working', 'issue'],
            'analysis': ['review', 'analyze', 'understand', 'examine'],
            'config': ['config', 'setup', 'environment', 'docker', 'compose'],
            'shell': ['bash', 'script', 'command', 'shell'],
            'install': ['install', 'setup', 'initialize'],
            'database': ['database', 'db', 'table', 'sql', 'postgres', 'mysql'],
            'api': ['api', 'endpoint', 'rest', 'json'],
            'test': ['test', 'pytest', 'testing'],
        }

        task_counts = Counter()

        for conv in conversations:
            text = json.dumps(conv).lower()
            for category, words in keywords.items():
                if any(word in text for word in words):
                    task_counts[category] += 1

        return dict(task_counts)

    def analyze_communication_style(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Analyze user's communication patterns"""
        user_messages = []

        for conv in conversations:
            # Extract user messages from conversation
            if isinstance(conv, dict) and 'messages' in conv:
                for msg in conv['messages']:
                    if isinstance(msg, dict) and msg.get('role') == 'user':
                        content = msg.get('content', '')
                        if isinstance(content, str):
                            user_messages.append(content)

        total = len(user_messages)
        if total == 0:
            return {}

        # Analyze query lengths
        lengths = [len(msg) for msg in user_messages]
        short = sum(1 for l in lengths if l < 50)
        medium = sum(1 for l in lengths if 50 <= l < 200)
        long_msgs = sum(1 for l in lengths if l >= 200)

        # Analyze politeness
        polite = sum(1 for msg in user_messages if any(word in msg.lower() for word in ['please', 'thanks', 'thank you']))

        # Analyze question vs command style
        questions = sum(1 for msg in user_messages if '?' in msg)

        return {
            'total_messages': total,
            'avg_length': sum(lengths) // total if total > 0 else 0,
            'short_queries': f"{(short/total)*100:.1f}%",
            'medium_queries': f"{(medium/total)*100:.1f}%",
            'long_queries': f"{(long_msgs/total)*100:.1f}%",
            'politeness_rate': f"{(polite/total)*100:.1f}%",
            'question_rate': f"{(questions/total)*100:.1f}%",
            'command_rate': f"{((total-questions)/total)*100:.1f}%",
        }

    def extract_tech_stack(self, conversations: List[Dict]) -> Dict[str, int]:
        """Extract mentioned technologies and their frequency"""
        tech_keywords = {
            'Python': r'\bpython\b',
            'PyCharm': r'\bpycharm\b',
            'pytest': r'\bpytest\b',
            'Docker': r'\bdocker\b',
            'PostgreSQL': r'\b(postgres|postgresql)\b',
            'MySQL': r'\bmysql\b',
            'Git': r'\bgit\b',
            'GitHub': r'\bgithub\b',
            'FastAPI': r'\bfastapi\b',
            'Flask': r'\bflask\b',
            'WSL': r'\bwsl\b',
            'JavaScript': r'\b(javascript|js)\b',
            'Node': r'\b(node|nodejs)\b',
            'Bash': r'\bbash\b',
        }

        tech_counts = Counter()
        text = json.dumps(conversations).lower()

        for tech, pattern in tech_keywords.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                tech_counts[tech] = len(matches)

        return dict(tech_counts.most_common(15))

    def find_pain_points(self, conversations: List[Dict]) -> List[str]:
        """Identify recurring pain points"""
        pain_indicators = [
            'not working',
            'still having issues',
            'error',
            'failed',
            'cannot',
            "can't",
            'problem',
            'issue',
        ]

        pain_points = []
        text = json.dumps(conversations).lower()

        for indicator in pain_indicators:
            count = text.count(indicator)
            if count > 5:
                pain_points.append(f"{indicator}: {count} occurrences")

        return pain_points

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        conversations = self.load_conversations()

        report = []
        report.append("=" * 80)
        report.append("GEMINI CLI CONVERSATION HISTORY ANALYSIS")
        report.append("=" * 80)
        report.append(f"\nTotal conversations: {len(conversations)}")
        report.append(f"History file: {self.history_file}")

        # Task frequency
        report.append("\n" + "-" * 80)
        report.append("TASK FREQUENCY ANALYSIS")
        report.append("-" * 80)
        tasks = self.analyze_task_frequency(conversations)
        for task, count in sorted(tasks.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(conversations)) * 100 if len(conversations) > 0 else 0
            report.append(f"{task:20s}: {count:4d} ({percentage:.1f}%)")

        # Communication style
        report.append("\n" + "-" * 80)
        report.append("COMMUNICATION STYLE ANALYSIS")
        report.append("-" * 80)
        style = self.analyze_communication_style(conversations)
        for key, value in style.items():
            report.append(f"{key:20s}: {value}")

        # Tech stack
        report.append("\n" + "-" * 80)
        report.append("TECHNOLOGY STACK")
        report.append("-" * 80)
        tech = self.extract_tech_stack(conversations)
        for technology, count in tech.items():
            report.append(f"{technology:20s}: {count:4d} mentions")

        # Pain points
        report.append("\n" + "-" * 80)
        report.append("PAIN POINTS (Recurring Issues)")
        report.append("-" * 80)
        pains = self.find_pain_points(conversations)
        for pain in pains:
            report.append(f"  - {pain}")

        report.append("\n" + "=" * 80)

        return "\n".join(report)


def main():
    analyzer = ConversationAnalyzer()
    report = analyzer.generate_report()
    print(report)

    # Optionally save to file
    output_file = Path("~/.gemini/conversation_analysis.txt").expanduser()
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
