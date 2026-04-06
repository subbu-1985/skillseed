import os

base_path = r"c:\Users\purni\Downloads\skillseed\frontend\lib\screens\dashboards\admin"
os.makedirs(base_path, exist_ok=True)

overview_content = """import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../services/api_service.dart';

class DashboardOverview extends StatefulWidget {
  const DashboardOverview({super.key});

  @override
  State<DashboardOverview> createState() => _DashboardOverviewState();
}

class _DashboardOverviewState extends State<DashboardOverview> {
  bool _isLoading = true;
  Map<String, dynamic> _stats = {};

  @override
  void initState() {
    super.initState();
    _fetchStats();
  }

  Future<void> _fetchStats() async {
    try {
      final token = await ApiService.getToken();
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/admin/stats'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        setState(() {
          _stats = json.decode(response.body);
          _isLoading = false;
        });
      }
    } catch (e) {
      print("Error loading stats: $e");
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Dashboard Overview',
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              _buildStatCard('Total Users', _stats['total_users']?.toString() ?? '0', Icons.people, Colors.blue),
              const SizedBox(width: 16),
              _buildStatCard('Students', _stats['total_students']?.toString() ?? '0', Icons.school, Colors.green),
              const SizedBox(width: 16),
              _buildStatCard('Mentors', _stats['total_mentors']?.toString() ?? '0', Icons.person_pin, Colors.orange),
              const SizedBox(width: 16),
              _buildStatCard('Pending Apps', _stats['pending_mentor_applications']?.toString() ?? '0', Icons.pending_actions, Colors.red),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(24),
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
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, size: 32, color: color),
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(color: Colors.grey[600], fontSize: 16)),
                const SizedBox(height: 4),
                Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 24)),
              ],
            )
          ],
        ),
      ),
    );
  }
}
"""

user_list_content = """import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../services/api_service.dart';

class UserListScreen extends StatefulWidget {
  const UserListScreen({super.key});

  @override
  State<UserListScreen> createState() => _UserListScreenState();
}

class _UserListScreenState extends State<UserListScreen> {
  bool _isLoading = true;
  List<dynamic> _users = [];

  @override
  void initState() {
    super.initState();
    _fetchUsers();
  }

  Future<void> _fetchUsers() async {
    try {
      final token = await ApiService.getToken();
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/admin/users'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        setState(() {
          _users = json.decode(response.body);
          _isLoading = false;
        });
      }
    } catch (e) {
      print("Error loading users: $e");
      setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleUserStatus(String id) async {
    try {
      final token = await ApiService.getToken();
      await http.post(
        Uri.parse('${ApiService.baseUrl}/admin/users/$id/toggle-active'),
        headers: {'Authorization': 'Bearer $token'},
      );
      _fetchUsers();
    } catch (e) {
      print("Error: $e");
    }
  }

  Future<void> _deleteUser(String id) async {
    try {
      final token = await ApiService.getToken();
      await http.delete(
        Uri.parse('${ApiService.baseUrl}/admin/users/$id'),
        headers: {'Authorization': 'Bearer $token'},
      );
      _fetchUsers();
    } catch (e) {
      print("Error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'User Management',
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: Container(
              color: Colors.white,
              child: ListView.builder(
                itemCount: _users.length,
                itemBuilder: (context, index) {
                  final user = _users[index];
                  return ListTile(
                    leading: CircleAvatar(
                      child: Text(user['email']?[0].toUpperCase() ?? 'U'),
                    ),
                    title: Text(user['name']?.isNotEmpty == true ? user['name'] : user['email']),
                    subtitle: Text('Role: ${user['role']} | Active: ${user['is_active']}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: Icon(user['is_active'] ? Icons.block : Icons.check_circle),
                          color: user['is_active'] ? Colors.orange : Colors.green,
                          onPressed: () => _toggleUserStatus(user['id']),
                          tooltip: user['is_active'] ? 'Disable' : 'Enable',
                        ),
                        IconButton(
                          icon: const Icon(Icons.delete, color: Colors.red),
                          onPressed: () => _deleteUser(user['id']),
                          tooltip: 'Delete User',
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          )
        ],
      ),
    );
  }
}
"""

mentor_content = """import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../services/api_service.dart';

class MentorApplicationsScreen extends StatefulWidget {
  const MentorApplicationsScreen({super.key});

  @override
  State<MentorApplicationsScreen> createState() => _MentorApplicationsScreenState();
}

class _MentorApplicationsScreenState extends State<MentorApplicationsScreen> {
  bool _isLoading = true;
  List<dynamic> _apps = [];

  @override
  void initState() {
    super.initState();
    _fetchApps();
  }

  Future<void> _fetchApps() async {
    try {
      final token = await ApiService.getToken();
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/admin/mentor-applications'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        setState(() {
          _apps = json.decode(response.body);
          _isLoading = false;
        });
      }
    } catch (e) {
      print("Error loading stats: $e");
      setState(() => _isLoading = false);
    }
  }

  Future<void> _approveMentor(String id) async {
    try {
      final token = await ApiService.getToken();
      await http.post(
        Uri.parse('${ApiService.baseUrl}/admin/mentor/$id/approve'),
        headers: {'Authorization': 'Bearer $token'},
      );
      _fetchApps();
    } catch (e) {
      print("Error: $e");
    }
  }

  Future<void> _rejectMentor(String id) async {
    try {
      final token = await ApiService.getToken();
      await http.post(
        Uri.parse('${ApiService.baseUrl}/admin/mentor/$id/reject'),
        headers: {'Authorization': 'Bearer $token'},
      );
      _fetchApps();
    } catch (e) {
      print("Error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Mentor Applications',
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: Container(
              color: Colors.white,
              child: ListView.builder(
                itemCount: _apps.length,
                itemBuilder: (context, index) {
                  final app = _apps[index];
                  return Card(
                    margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(app['name']?.isNotEmpty == true ? app['name'] : app['email'], 
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)
                              ),
                              Chip(
                                label: Text(app['status'].toString().toUpperCase()),
                                backgroundColor: app['status'] == 'pending' ? Colors.orange[100] : (app['status'] == 'approved' ? Colors.green[100] : Colors.red[100]),
                              )
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text("Expertise: ${app['expertise'] ?? 'Not provided'}"),
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              if (app['status'] == 'pending') ...[
                                ElevatedButton.icon(
                                  icon: const Icon(Icons.check),
                                  label: const Text("Approve"),
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                                  onPressed: () => _approveMentor(app['id']),
                                ),
                                const SizedBox(width: 8),
                                ElevatedButton.icon(
                                  icon: const Icon(Icons.close),
                                  label: const Text("Reject"),
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                                  onPressed: () => _rejectMentor(app['id']),
                                ),
                              ]
                            ],
                          )
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          )
        ],
      ),
    );
  }
}
"""

with open(os.path.join(base_path, "dashboard_overview.dart"), "w") as f:
    f.write(overview_content)

with open(os.path.join(base_path, "user_list_screen.dart"), "w") as f:
    f.write(user_list_content)

with open(os.path.join(base_path, "mentor_applications_screen.dart"), "w") as f:
    f.write(mentor_content)
