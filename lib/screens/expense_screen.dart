import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class ExpenseScreen extends StatefulWidget {
  const ExpenseScreen({Key? key}) : super(key: key);

  @override
  State<ExpenseScreen> createState() => _ExpenseScreenState();
}

class _ExpenseScreenState extends State<ExpenseScreen> {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  double totalExpenses = 0;
  double personalExpenses = 0;
  double businessExpenses = 0;
  List<Map<String, dynamic>> expenses = [];

  @override
  void initState() {
    super.initState();
    _listenToExpenses();
  }

  void _listenToExpenses() {
    final user = _auth.currentUser;
    if (user == null) return;

    _firestore
        .collection('users')
        .doc(user.uid)
        .collection('expenses')
        .orderBy('date', descending: true)
        .snapshots()
        .listen((snapshot) {
      final docs = snapshot.docs
          .map((doc) => {
                'id': doc.id,
                ...doc.data(),
              })
          .toList();

      double total = 0;
      double personal = 0;
      double business = 0;

      for (var e in docs) {
        final amount = ((e['amount'] ?? 0) as num).toDouble();
        total += amount;

        if (e['type'] == 'personal') {
          personal += amount;
        } else if (e['type'] == 'business') {
          business += amount;
        }
      }

      setState(() {
        expenses = docs;
        totalExpenses = total;
        personalExpenses = personal;
        businessExpenses = business;
      });
    });
  }

  Future<void> _addOrEditExpense({
    String? docId,
    String initialItem = '',
    double? initialAmount,
    String initialType = 'personal',
    String initialCategory = '',
    String initialNote = '',
  }) async {
    final user = _auth.currentUser;
    if (user == null) return;

    final itemController = TextEditingController(text: initialItem);
    final amountController = TextEditingController(
      text: initialAmount != null ? initialAmount.toString() : '',
    );
    final categoryController = TextEditingController(text: initialCategory);
    final noteController = TextEditingController(text: initialNote);
    String expenseType = initialType;

    final result = await showDialog<bool>(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: Text(docId == null ? 'Add Expense' : 'Edit Expense'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: itemController,
                      decoration: const InputDecoration(labelText: 'Item'),
                    ),
                    TextField(
                      controller: amountController,
                      decoration:
                          const InputDecoration(labelText: 'Amount (Rs.)'),
                      keyboardType:
                          const TextInputType.numberWithOptions(decimal: true),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Text('Type:'),
                        const SizedBox(width: 12),
                        DropdownButton<String>(
                          value: expenseType,
                          items: const [
                            DropdownMenuItem(
                              value: 'personal',
                              child: Text('Personal'),
                            ),
                            DropdownMenuItem(
                              value: 'business',
                              child: Text('Business'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value != null) {
                              setDialogState(() {
                                expenseType = value;
                              });
                            }
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: categoryController,
                      decoration: const InputDecoration(
                          labelText: 'Category (optional)'),
                    ),
                    TextField(
                      controller: noteController,
                      decoration:
                          const InputDecoration(labelText: 'Note (optional)'),
                      maxLines: 2,
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Cancel'),
                ),
                TextButton(
                  onPressed: () {
                    if (itemController.text.isNotEmpty &&
                        amountController.text.isNotEmpty) {
                      Navigator.pop(context, true);
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Please fill item and amount'),
                        ),
                      );
                    }
                  },
                  child: const Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );

    if (result != true) return;

    final amount = double.tryParse(amountController.text) ?? 0;

    final data = {
      'item': itemController.text.trim(),
      'amount': amount,
      'type': expenseType,
      'category': categoryController.text.trim(),
      'note': noteController.text.trim(),
      'date': FieldValue.serverTimestamp(),
    };

    final ref = _firestore
        .collection('users')
        .doc(user.uid)
        .collection('expenses');

    try {
      if (docId == null) {
        await ref.add(data);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Expense added successfully')),
        );
      } else {
        await ref.doc(docId).update(data);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Expense updated successfully')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  Future<void> _deleteExpense(String docId) async {
    final user = _auth.currentUser;
    if (user == null) return;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete expense?'),
        content: const Text('Are you sure you want to delete this expense?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _firestore
            .collection('users')
            .doc(user.uid)
            .collection('expenses')
            .doc(docId)
            .delete();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Expense deleted successfully')),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting expense: $e')),
        );
      }
    }
  }

  Future<void> _signOut() async {
    await _auth.signOut();
  }

  @override
  Widget build(BuildContext context) {
    final user = _auth.currentUser;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Money Monitor'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _signOut,
          ),
        ],
      ),
      body: Column(
        children: [
          // Summary Cards
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // Total Expenses Card
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Total Expenses',
                          style: TextStyle(fontSize: 16),
                        ),
                        Text(
                          'Rs. ${totalExpenses.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                // Personal vs Business Row
                Row(
                  children: [
                    Expanded(
                      child: Card(
                        color: Colors.green.shade50,
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            children: [
                              const Text(
                                'Personal',
                                style: TextStyle(fontSize: 14),
                              ),
                              Text(
                                'Rs. ${personalExpenses.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Card(
                        color: Colors.orange.shade50,
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            children: [
                              const Text(
                                'Business',
                                style: TextStyle(fontSize: 14),
                              ),
                              Text(
                                'Rs. ${businessExpenses.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.orange,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Expenses List
          Expanded(
            child: expenses.isEmpty
                ? const Center(
                    child: Text('No expenses yet. Add one to get started!'),
                  )
                : ListView.builder(
                    itemCount: expenses.length,
                    itemBuilder: (context, index) {
                      final expense = expenses[index];
                      final amount = ((expense['amount'] ?? 0) as num).toDouble();
                      final type = expense['type'] ?? 'personal';
                      final item = expense['item'] ?? 'Unknown';
                      final category = expense['category'] ?? 'Uncategorized';
                      final note = expense['note'] ?? '';
                      final docId = expense['id'];

                      return Card(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        child: ListTile(
                          title: Text(item),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Category: $category',
                                style: const TextStyle(fontSize: 12),
                              ),
                              if (note.isNotEmpty)
                                Text(
                                  'Note: $note',
                                  style: const TextStyle(fontSize: 12),
                                ),
                              Text(
                                'Type: ${type[0].toUpperCase()}${type.substring(1)}',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: type == 'business'
                                      ? Colors.orange
                                      : Colors.green,
                                ),
                              ),
                            ],
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                'Rs. ${amount.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                              PopupMenuButton<String>(
                                onSelected: (value) {
                                  if (value == 'edit') {
                                    _addOrEditExpense(
                                      docId: docId,
                                      initialItem: item,
                                      initialAmount: amount,
                                      initialType: type,
                                      initialCategory: category,
                                      initialNote: note,
                                    );
                                  } else if (value == 'delete') {
                                    _deleteExpense(docId);
                                  }
                                },
                                itemBuilder: (BuildContext context) => [
                                  const PopupMenuItem(
                                    value: 'edit',
                                    child: Text('Edit'),
                                  ),
                                  const PopupMenuItem(
                                    value: 'delete',
                                    child: Text('Delete'),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _addOrEditExpense(),
        child: const Icon(Icons.add),
      ),
    );
  }

  @override
  void dispose() {
    super.dispose();
  }
}
