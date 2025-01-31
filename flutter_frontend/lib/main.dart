import 'package:flutter/material.dart';
import 'chat.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
            brightness: Brightness.dark,
            seedColor: Colors.grey,
            contrastLevel: 0.25,
            dynamicSchemeVariant: DynamicSchemeVariant.fidelity),
        useMaterial3: true,
      ),
      home: const ChatPage(title: 'MyRag'),
    );
  }
}
