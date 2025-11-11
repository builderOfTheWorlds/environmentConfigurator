#!/usr/bin/env python3
"""
Daily Conversation History Analyzer for Gemini CLI
Runs comprehensive analysis of all conversation history and logs results
"""

import json
import re
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple


class ComprehensiveAnalyzer:
    def __init__(self, gemini_dir: str = "~/.gemini"):
        self.gemini_dir = Path(gemini_dir).expanduser()
        self.main_history = self.gemini_dir / "history.jsonl"
        self.projects_dir = self.gemini_dir / "projects"
        self.log_dir = self.gemini_dir / "analysis_logs"
        self.log_dir.mkdir(exist_ok=True)

        self.timestamp = datetime.now()
        self.log_file = self.log_dir / f"analysis_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.log"

    def log(self, message: str, level: str = "INFO"):
        """Log message to both file and stdout"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        with open(self.log_file, 'a') as f:
            f.write(log_message + "\n")

    def load_all_conversations(self) -> Tuple[List[Dict], Dict[str, int]]:
        """Load conversations from main history and all project files"""
        all_conversations = []
        sources = defaultdict(int)

        # Load main history
        if self.main_history.exists():
            self.log(f"Loading main history: {self.main_history}")
            with open(self.main_history, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_conversations.append(json.loads(line))
                        sources['main_history'] += 1
            self.log(f"Loaded {sources['main_history']} conversations from main history")

        # Load project-specific conversations
        if self.projects_dir.exists():
            project_files = list(self.projects_dir.rglob("*.jsonl"))
            self.log(f"Found {len(project_files)} project conversation files")

            for project_file in project_files:
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                all_conversations.append(json.loads(line))
                                sources['project_conversations'] += 1
                except Exception as e:
                    self.log(f"Error reading {project_file}: {e}", "WARNING")

            self.log(f"Loaded {sources['project_conversations']} project conversations")

        return all_conversations, dict(sources)

    def analyze_task_frequency(self, conversations: List[Dict]) -> Dict[str, int]:
        """Analyze frequency of different task types"""
        keywords = {
            'git': ['git', 'commit', 'branch', 'push', 'pull', 'merge', 'clone'],
            'file_ops': ['create', 'modify', 'delete', 'move', 'file', 'write', 'edit'],
            'debug': ['error', 'bug', 'debug', 'fix', 'not working', 'issue', 'broken'],
            'analysis': ['review', 'analyze', 'understand', 'examine', 'explain'],
            'config': ['config', 'setup', 'environment', 'docker', 'compose'],
            'shell': ['bash', 'script', 'command', 'shell', 'terminal'],
            'install': ['install', 'setup', 'initialize', 'dependency'],
            'database': ['database', 'db', 'table', 'sql', 'postgres', 'mysql', 'query'],
            'api': ['api', 'endpoint', 'rest', 'json', 'http', 'request'],
            'test': ['test', 'pytest', 'testing', 'unittest'],
            'refactor': ['refactor', 'reorganize', 'restructure', 'cleanup'],
            'performance': ['optimize', 'performance', 'speed', 'slow', 'parallel', 'async'],
        }

        task_counts = Counter()
        text = json.dumps(conversations).lower()

        for category, words in keywords.items():
            count = sum(text.count(word) for word in words)
            if count > 0:
                task_counts[category] = count

        return dict(task_counts)

    def analyze_communication_style(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Analyze user's communication patterns"""
        user_messages = []

        for conv in conversations:
            if isinstance(conv, dict):
                # Handle different conversation formats
                if 'messages' in conv:
                    for msg in conv['messages']:
                        if isinstance(msg, dict) and msg.get('role') == 'user':
                            content = msg.get('content', '')
                            if isinstance(content, str) and content.strip():
                                user_messages.append(content)
                elif 'role' in conv and conv.get('role') == 'user':
                    content = conv.get('content', '')
                    if isinstance(content, str) and content.strip():
                        user_messages.append(content)

        total = len(user_messages)
        if total == 0:
            return {'total_messages': 0}

        # Analyze query lengths
        lengths = [len(msg) for msg in user_messages]
        short = sum(1 for l in lengths if l < 50)
        medium = sum(1 for l in lengths if 50 <= l < 200)
        long_msgs = sum(1 for l in lengths if l >= 200)

        # Analyze politeness
        polite = sum(1 for msg in user_messages
                    if any(word in msg.lower() for word in ['please', 'thanks', 'thank you']))

        # Analyze question vs command style
        questions = sum(1 for msg in user_messages if '?' in msg)

        return {
            'total_messages': total,
            'avg_length': sum(lengths) // total if total > 0 else 0,
            'short_queries_pct': f"{(short/total)*100:.1f}%",
            'medium_queries_pct': f"{(medium/total)*100:.1f}%",
            'long_queries_pct': f"{(long_msgs/total)*100:.1f}%",
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
            'TypeScript': r'\btypescript\b',
            'Node': r'\b(node|nodejs)\b',
            'Bash': r'\bbash\b',
            'Redis': r'\bredis\b',
            'MongoDB': r'\bmongo(db)?\b',
        }

        tech_counts = Counter()
        text = json.dumps(conversations).lower()

        for tech, pattern in tech_keywords.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                tech_counts[tech] = len(matches)

        return dict(tech_counts.most_common(20))

    def find_pain_points(self, conversations: List[Dict]) -> Dict[str, int]:
        """Identify recurring pain points"""
        pain_indicators = {
            'not working': 0,
            'still having issues': 0,
            'error': 0,
            'failed': 0,
            'cannot': 0,
            "can't": 0,
            'problem': 0,
            'issue': 0,
            'broken': 0,
            'does not work': 0,
            "doesn't work": 0,
        }

        text = json.dumps(conversations).lower()

        for indicator in pain_indicators:
            pain_indicators[indicator] = text.count(indicator)

        # Only return indicators with significant occurrences
        return {k: v for k, v in pain_indicators.items() if v > 3}

    def extract_key_quotes(self, conversations: List[Dict], limit: int = 10) -> List[str]:
        """Extract important user quotes/preferences"""
        user_messages = []

        for conv in conversations:
            if isinstance(conv, dict):
                if 'messages' in conv:
                    for msg in conv['messages']:
                        if isinstance(msg, dict) and msg.get('role') == 'user':
                            content = msg.get('content', '')
                            if isinstance(content, str) and content.strip():
                                user_messages.append(content)

        # Look for preference-indicating phrases
        preference_keywords = [
            'i want',
            'i need',
            'please',
            'can you',
            'do not',
            "don't",
            'always',
            'never',
            'prefer',
        ]

        important_messages = []
        for msg in user_messages:
            msg_lower = msg.lower()
            # Look for messages with preferences and sufficient length
            if any(kw in msg_lower for kw in preference_keywords) and 20 < len(msg) < 200:
                important_messages.append(msg.strip())

        # Return unique messages, limited
        seen = set()
        unique_quotes = []
        for msg in important_messages:
            if msg not in seen and len(unique_quotes) < limit:
                seen.add(msg)
                unique_quotes.append(msg)

        return unique_quotes

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        self.log("Starting comprehensive conversation analysis")

        conversations, sources = self.load_all_conversations()
        total_convs = len(conversations)

        self.log(f"Total conversations loaded: {total_convs}")

        report = []
        report.append("=" * 100)
        report.append("GEMINI CLI COMPREHENSIVE CONVERSATION ANALYSIS")
        report.append("=" * 100)
        report.append(f"\nAnalysis Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Conversations: {total_convs}")
        report.append(f"\nSources:")
        for source, count in sources.items():
            report.append(f"  - {source}: {count}")

        # Task frequency
        self.log("Analyzing task frequency")
        report.append("\n" + "-" * 100)
        report.append("TASK FREQUENCY ANALYSIS")
        report.append("-" * 100)
        tasks = self.analyze_task_frequency(conversations)
        for task, count in sorted(tasks.items(), key=lambda x: x[1], reverse=True):
            report.append(f"{task:20s}: {count:6d} mentions")

        # Communication style
        self.log("Analyzing communication style")
        report.append("\n" + "-" * 100)
        report.append("COMMUNICATION STYLE ANALYSIS")
        report.append("-" * 100)
        style = self.analyze_communication_style(conversations)
        for key, value in style.items():
            report.append(f"{key:25s}: {value}")

        # Tech stack
        self.log("Analyzing technology stack")
        report.append("\n" + "-" * 100)
        report.append("TECHNOLOGY STACK")
        report.append("-" * 100)
        tech = self.extract_tech_stack(conversations)
        for technology, count in tech.items():
            report.append(f"{technology:20s}: {count:6d} mentions")

        # Pain points
        self.log("Identifying pain points")
        report.append("\n" + "-" * 100)
        report.append("PAIN POINTS (Recurring Issues)")
        report.append("-" * 100)
        pains = self.find_pain_points(conversations)
        for pain, count in sorted(pains.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  '{pain}': {count} occurrences")

        # Key quotes
        self.log("Extracting key user preferences")
        report.append("\n" + "-" * 100)
        report.append("KEY USER PREFERENCES (Sample Quotes)")
        report.append("-" * 100)
        quotes = self.extract_key_quotes(conversations)
        for i, quote in enumerate(quotes, 1):
            report.append(f"{i:2d}. \"{quote}\" ")

        report.append("\n" + "=" * 100)
        report.append(f"Log file: {self.log_file}")
        report.append("=" * 100)

        return "\n".join(report)

    def run(self):
        """Execute the analysis and save results"""
        try:
            self.log("=" * 50)
            self.log("STARTING DAILY CONVERSATION ANALYSIS")
            self.log("=" * 50)

            report = self.generate_report()

            # Save report to dated file
            report_file = self.log_dir / f"report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            self.log(f"Report saved to: {report_file}")

            # Also save as latest report
            latest_report = self.gemini_dir / "latest_analysis.txt"
            with open(latest_report, 'w', encoding='utf-8') as f:
                f.write(report)

            self.log(f"Latest report saved to: {latest_report}")

            # Print report to stdout
            print("\n" + report)

            self.log("=" * 50)
            self.log("ANALYSIS COMPLETE")
            self.log("=" * 50)

            return 0

        except Exception as e:
            self.log(f"FATAL ERROR: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return 1


def main():
    analyzer = ComprehensiveAnalyzer()
    return analyzer.run()


if __name__ == "__main__":
    sys.exit(main())
