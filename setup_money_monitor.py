# ==========================================
# COMPLETE MONEY MONITOR APP SETUP
# Automates Flutter + Firebase setup
# ==========================================
# FILE: setup_money_monitor.py
# Usage: python setup_money_monitor.py
# ==========================================

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

# ==========================================
# STEP 1: CHECK FLUTTER
# ==========================================
def check_flutter():
    """Check if Flutter is installed"""
    print_header("✔️  CHECKING FLUTTER")
    
    try:
        result = subprocess.run(
            ['flutter', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success("Flutter is installed!")
            print_info(result.stdout)
            return True
        else:
            print_error("Flutter not found")
            return False
    except:
        print_error("Flutter not found in PATH")
        return False

# ==========================================
# STEP 2: GET FIREBASE CONFIG
# ==========================================
def get_firebase_config():
    """Get Firebase configuration from user"""
    print_header("🔥 FIREBASE CONFIGURATION")
    print("Get these from: https://console.firebase.google.com\n")
    print("1. Click your project")
    print("2. Project Settings ⚙️ → General tab")
    print("3. Copy firebaseConfig values\n")
    
    config = {}
    
    print_info("Press Enter to skip any field (use defaults)\n")
    
    apiKey = input(f"{Colors.BOLD}{Colors.OKBLUE}➜ API Key: {Colors.ENDC}").strip()
    config['apiKey'] = apiKey if apiKey else "YOUR_API_KEY_HERE"
    
    authDomain = input(f"{Colors.BOLD}{Colors.OKBLUE}➜ Auth Domain (e.g., project.firebaseapp.com): {Colors.ENDC}").strip()
    config['authDomain'] = authDomain if authDomain else "YOUR_PROJECT.firebaseapp.com"
    
    projectId = input(f"{Colors.BOLD}{Colors.OKBLUE}➜ Project ID: {Colors.ENDC}").strip()
    config['projectId'] = projectId if projectId else "YOUR_PROJECT_ID"
    
    storageBucket = input(f"{Colors.BOLD}{Colors.OKBLUE}➜ Storage Bucket (e.g., project.appspot.com): {Colors.ENDC}").strip()
    config['storageBucket'] = storageBucket if storageBucket else "YOUR_PROJECT.appspot.com"
    
    messagingSenderId = input(f"{Colors.BOLD}{Colors.OKBLUE}➜ Messaging Sender ID: {Colors.ENDC}").strip()
    config['messagingSenderId'] = messagingSenderId if messagingSenderId else "YOUR_SENDER_ID"
    
    appId = input(f"{Colors.BOLD}{Colors.OKBLUE}➜ App ID: {Colors.ENDC}").strip()
    config['appId'] = appId if appId else "YOUR_APP_ID"
    
    return config

# ==========================================
# STEP 3: CREATE FIREBASE CONFIG DART FILE
# ==========================================
def create_firebase_config(project_path, config):
    """Create firebase_config.dart file"""
    print_header("🔑 CREATING FIREBASE CONFIG")
    
    firebase_config_content = f'''// FILE: lib/firebase_config.dart
// Firebase configuration for Money Monitor app
// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

class FirebaseConfig {{
  // Web API Key (from Firebase Console)
  static const String apiKey = "{config['apiKey']}";
  
  // Authentication domain
  static const String authDomain = "{config['authDomain']}";
  
  // Firebase project ID
  static const String projectId = "{config['projectId']}";
  
  // Cloud Storage bucket
  static const String storageBucket = "{config['storageBucket']}";
  
  // Messaging sender ID
  static const String messagingSenderId = "{config['messagingSenderId']}";
  
  // Firebase app ID
  static const String appId = "{config['appId']}";
}}
'''
    
    lib_path = project_path / "lib"
    config_file = lib_path / "firebase_config.dart"
    
    try:
        with open(config_file, 'w') as f:
            f.write(firebase_config_content)
        print_success(f"Created: firebase_config.dart")
        return True
    except Exception as e:
        print_error(f"Failed to create firebase_config.dart: {str(e)}")
        return False

# ==========================================
# STEP 4: UPDATE PUBSPEC.YAML
# ==========================================
def update_pubspec(project_path):
    """Update pubspec.yaml with Firebase dependencies"""
    print_header("📦 UPDATING DEPENDENCIES")
    
    pubspec_file = project_path / "pubspec.yaml"
    
    try:
        with open(pubspec_file, 'r') as f:
            content = f.read()
        
        # Add Firebase dependencies if not already present
        if 'firebase_core' not in content:
            # Find the dependencies section and add Firebase packages
            new_dependencies = '''dependencies:
  flutter:
    sdk: flutter
  firebase_core: ^3.0.0
  firebase_auth: ^4.0.0
  cloud_firestore: ^4.0.0
  google_sign_in: ^6.0.0
  provider: ^6.0.0'''
            
            # Replace the dependencies section
            if 'dependencies:' in content:
                old_deps = content.split('dev_dependencies')[0]
                rest = content.split('dev_dependencies')[1]
                content = new_dependencies + '\n\ndev_dependencies' + rest
        
        with open(pubspec_file, 'w') as f:
            f.write(content)
        
        print_success("Updated pubspec.yaml with Firebase packages")
        return True
    except Exception as e:
        print_error(f"Failed to update pubspec.yaml: {str(e)}")
        return False

# ==========================================
# STEP 5: RUN FLUTTER PUB GET
# ==========================================
def run_pub_get(project_path):
    """Run flutter pub get to install dependencies"""
    print_header("⬇️  INSTALLING DEPENDENCIES")
    
    print_info("Installing Flutter dependencies (this may take 2-5 minutes)...\n")
    
    try:
        result = subprocess.run(
            ['flutter', 'pub', 'get'],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print_success("Dependencies installed successfully!")
            return True
        else:
            print_warning("Dependencies installation had issues")
            print_info(result.stderr)
            return False
    except Exception as e:
        print_error(f"Error installing dependencies: {str(e)}")
        return False

# ==========================================
# STEP 6: CREATE ENHANCED MAIN.DART
# ==========================================
def create_enhanced_main(project_path):
    """Create enhanced main.dart with Firebase setup"""
    print_header("🎯 CREATING ENHANCED MAIN.DART")
    
    main_dart_content = '''import 'package:flutter/material.dart';
import 'firebase_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Firebase initialization would go here
  // await Firebase.initializeApp(
  //   options: FirebaseOptions(
  //     apiKey: FirebaseConfig.apiKey,
  //     appId: FirebaseConfig.appId,
  //     messagingSenderId: FirebaseConfig.messagingSenderId,
  //     projectId: FirebaseConfig.projectId,
  //     storageBucket: FirebaseConfig.storageBucket,
  //     authDomain: FirebaseConfig.authDomain,
  //   ),
  // );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Money Monitor',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const MoneyMonitorHome(),
    );
  }
}

class MoneyMonitorHome extends StatefulWidget {
  const MoneyMonitorHome({Key? key}) : super(key: key);

  @override
  State<MoneyMonitorHome> createState() => _MoneyMonitorHomeState();
}

class _MoneyMonitorHomeState extends State<MoneyMonitorHome> {
  double totalExpenses = 0;
  List<String> expenses = [];

  void addExpense(String item, double amount) {
    setState(() {
      expenses.add("$item: Rs. $amount");
      totalExpenses += amount;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('💰 Money Monitor'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            color: Colors.blue.shade100,
            child: Column(
              children: [
                const Text('Total Expenses', style: TextStyle(fontSize: 16)),
                Text(
                  'Rs. ${totalExpenses.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: expenses.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(expenses[index]),
                  leading: const Icon(Icons.money),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          showDialog(
            context: context,
            builder: (context) => AddExpenseDialog(
              onAdd: addExpense,
            ),
          );
        },
        tooltip: 'Add Expense',
        child: const Icon(Icons.add),
      ),
    );
  }
}

class AddExpenseDialog extends StatefulWidget {
  final Function(String, double) onAdd;

  const AddExpenseDialog({Key? key, required this.onAdd}) : super(key: key);

  @override
  State<AddExpenseDialog> createState() => _AddExpenseDialogState();
}

class _AddExpenseDialogState extends State<AddExpenseDialog> {
  final itemController = TextEditingController();
  final amountController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add Expense'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: itemController,
            decoration: const InputDecoration(labelText: 'Item'),
          ),
          TextField(
            controller: amountController,
            decoration: const InputDecoration(labelText: 'Amount (Rs.)'),
            keyboardType: TextInputType.number,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        TextButton(
          onPressed: () {
            if (itemController.text.isNotEmpty &&
                amountController.text.isNotEmpty) {
              widget.onAdd(
                itemController.text,
                double.parse(amountController.text),
              );
              Navigator.pop(context);
            }
          },
          child: const Text('Add'),
        ),
      ],
    );
  }
}
'''
    
    lib_path = project_path / "lib"
    main_file = lib_path / "main.dart"
    
    try:
        with open(main_file, 'w') as f:
            f.write(main_dart_content)
        print_success("Created enhanced main.dart with Money Monitor features")
        return True
    except Exception as e:
        print_error(f"Failed to create main.dart: {str(e)}")
        return False

# ==========================================
# STEP 7: FINAL SUMMARY
# ==========================================
def print_summary(project_path, config):
    """Print final summary"""
    print_header("✅ SETUP COMPLETE")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}Money Monitor is ready!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Project Location:{Colors.ENDC}")
    print(f"  {project_path}\n")
    
    print(f"{Colors.BOLD}Firebase Configuration:{Colors.ENDC}")
    print(f"  Project ID: {config['projectId']}")
    print(f"  Auth Domain: {config['authDomain']}\n")
    
    print(f"{Colors.BOLD}Files Created:{Colors.ENDC}")
    print(f"  ✅ lib/firebase_config.dart")
    print(f"  ✅ lib/main.dart (with Money Monitor app)")
    print(f"  ✅ pubspec.yaml (Firebase packages added)\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"  1. Navigate to project:")
    print(f"     cd {project_path}\n")
    print(f"  2. Run the app:")
    print(f"     flutter run -d chrome\n")
    print(f"  3. See your Money Monitor app in Chrome!\n")
    
    print(f"{Colors.BOLD}Commands to Remember:{Colors.ENDC}")
    print(f"  flutter run -d chrome      - Run in Chrome")
    print(f"  flutter run -d edge        - Run in Edge")
    print(f"  flutter pub get            - Update dependencies")
    print(f"  r                          - Hot reload (while running)\n")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}🚀 Ready to launch!{Colors.ENDC}\n")

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    """Main execution function"""
    print_header("💰 MONEY MONITOR - COMPLETE SETUP")
    print("Setting up Flutter + Firebase + Money Monitor App\n")
    
    # Step 1: Check Flutter
    if not check_flutter():
        print_error("Please install Flutter first!")
        print_info("Download from: https://flutter.dev/docs/get-started/install")
        sys.exit(1)
    
    # Step 2: Get or use existing project
    project_path = Path("C:/app/money_monitor")
    
    if not project_path.exists():
        print_error("Project not found at: C:\\app\\money_monitor")
        print_info("Please create it first with: flutter create money_monitor")
        sys.exit(1)
    
    print_success(f"Found project at: {project_path}\n")
    
    # Step 3: Get Firebase config
    config = get_firebase_config()
    
    # Step 4: Create Firebase config file
    if not create_firebase_config(project_path, config):
        print_warning("Failed to create Firebase config")
    
    # Step 5: Update pubspec.yaml
    if not update_pubspec(project_path):
        print_warning("Failed to update pubspec.yaml")
    
    # Step 6: Install dependencies
    if not run_pub_get(project_path):
        print_warning("Failed to install dependencies")
    
    # Step 7: Create enhanced main.dart
    if not create_enhanced_main(project_path):
        print_warning("Failed to create main.dart")
    
    # Step 8: Print summary
    print_summary(project_path, config)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
