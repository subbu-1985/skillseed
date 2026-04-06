import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:skillseed_frontend/screens/dashboards/admin/user_list_screen.dart';

void main() {
  testWidgets('Test UserListScreen layouts correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 800,
            height: 600,
            child: UserListScreen(),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byType(UserListScreen), findsOneWidget);
  });
}
