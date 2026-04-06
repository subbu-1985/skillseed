import os
import re

base_path = r"c:\Users\purni\Downloads\skillseed\frontend\lib\screens\dashboards\admin"
os.makedirs(base_path, exist_ok=True)

def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def generate_static_screen(class_name, title, icon, description, elements):
    elements_code = ""
    if elements:
        elements_code = """
                    const SizedBox(height: 32),
                    const Text('Planned Layout & Features:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    const SizedBox(height: 16),
"""
        for el in elements:
            elements_code += f"                    ListTile(leading: const Icon(Icons.check_circle, color: Colors.deepPurple), title: Text('{el}')),\n"

    return f"""import 'package:flutter/material.dart';

class {class_name} extends StatelessWidget {{
  const {class_name}({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '{title}',
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(32),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 5),
                  )
                ],
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Icon({icon}, size: 80, color: Colors.deepPurple.withOpacity(0.5)),
                    const SizedBox(height: 24),
                    Text(
                      '{description}',
                      style: TextStyle(fontSize: 18, color: Colors.grey[800]),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'This module is currently under development.',
                      style: TextStyle(color: Colors.grey[500]),
                    ),
                    {elements_code}
                  ],
                ),
              ),
            ),
          )
        ],
      ),
    );
  }}
}}
"""

screens = [
    ("SkillsManagementScreen", "Skills Management", "Icons.lightbulb_outline", "Manage the core soft skills offered on the platform.", ["Create, Edit, Delete Skills", "View modules under each skill", "Skill layout: Name | Description | Modules | Status | Action"]),
    ("ModulesManagementScreen", "Modules Management", "Icons.view_module_outlined", "Manage lessons inside each skill.", ["Create, Edit, Delete Modules", "Attach Content (Videos, activities, quizzes)", "Module layout: Name | Skill | Activities | Quizzes | Status | Action"]),
    ("ContentManagementScreen", "Content Management", "Icons.video_library_outlined", "Manage videos, activities, puzzles, and games.", ["Upload videos and documents (MinIO/S3)", "Add activities and puzzles", "Content layout: Title | Module | Type | Uploaded By | Status | Action"]),
    ("LiveSessionsScreen", "Live Sessions", "Icons.event_outlined", "Manage mentor-led live classes.", ["View session details", "Cancel / Reschedule sessions", "Monitor attendance linked with Jitsi Meet"]),
    ("NotificationsScreen", "Notifications", "Icons.notifications_outlined", "Send announcements to users.", ["Broadcast platform announcements and session reminders", "Target Audience: All / Students / Mentors", "Notification Form: Title, Message, Audience"]),
    ("SubscriptionsScreen", "Subscriptions", "Icons.payment_outlined", "Manage premium plans.", ["Create/Edit subscription plans (Free/Premium)", "Activate/Deactivate plans", "View subscribed students"]),
    ("PaymentsScreen", "Payments", "Icons.account_balance_wallet_outlined", "Track payments and transactions.", ["Track Student payments", "Review Amount, Gateway, Status, Date"]),
    ("AnalyticsScreen", "Analytics", "Icons.analytics_outlined", "View platform performance metrics.", ["User Growth (Line Chart)", "Skill Popularity (Bar Chart)", "Module Completion Rate", "Quiz Performance", "Revenue Analytics (Pie Chart)"]),
    ("SettingsScreen", "Settings", "Icons.settings_outlined", "Control platform configuration.", ["Platform Name & Default Language", "Max Video / File Upload Size", "Session Duration Configuration"]),
    ("AdminLogsScreen", "Admin Logs", "Icons.history_outlined", "Track all administrative actions.", ["View actions (e.g., approved mentor, deleted module)", "Stored in admin_logs table"]),
]

for class_name, title, icon, desc, elements in screens:
    filename = camel_to_snake(class_name) + ".dart"
    with open(os.path.join(base_path, filename), "w") as f:
        f.write(generate_static_screen(class_name, title, icon, desc, elements))

print("Detailed static screens generated successfully.")
