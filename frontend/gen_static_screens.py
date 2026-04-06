import os

base_path = r"c:\Users\purni\Downloads\skillseed\frontend\lib\screens\dashboards\admin"
os.makedirs(base_path, exist_ok=True)

def generate_static_screen(class_name, title, icon):
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
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon({icon}, size: 80, color: Colors.grey[400]),
                    const SizedBox(height: 16),
                    Text(
                      '{title} module is currently under development.',
                      style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'This feature will be available in a future update.',
                      style: TextStyle(color: Colors.grey[500]),
                    ),
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
    ("SkillsManagementScreen", "Skills Management", "Icons.lightbulb_outline", "skills_management_screen.dart"),
    ("ModulesManagementScreen", "Modules Management", "Icons.view_module_outlined", "modules_management_screen.dart"),
    ("ContentManagementScreen", "Content Management", "Icons.video_library_outlined", "content_management_screen.dart"),
    ("LiveSessionsScreen", "Live Sessions Management", "Icons.event_outlined", "live_sessions_screen.dart"),
    ("NotificationsScreen", "Notifications", "Icons.notifications_outlined", "notifications_screen.dart"),
    ("SubscriptionsScreen", "Subscriptions Management", "Icons.payment_outlined", "subscriptions_screen.dart"),
    ("AnalyticsScreen", "Platform Analytics", "Icons.analytics_outlined", "analytics_screen.dart"),
    ("SettingsScreen", "System Settings", "Icons.settings_outlined", "settings_screen.dart"),
]

for class_name, title, icon, filename in screens:
    with open(os.path.join(base_path, filename), "w") as f:
        f.write(generate_static_screen(class_name, title, icon))

print("Static screens generated successfully.")
