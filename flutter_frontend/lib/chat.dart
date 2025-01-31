// ignore_for_file: prefer_const_constructors, prefer_const_literals_to_create_immutables

import 'package:flutter/material.dart';
import 'chat_message.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key, required this.title});

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  bool _inConversation = false;
  final _conversation = <String>[];
  late Future<String> _futureData;
  String _data = "";

  // Simulate a network request by delaying for 2 seconds
  Future<void> fetchData() async {
    await Future.delayed(Duration(seconds: 2));
    _onLLMResponse("LLM res loaded");
  }

  final TextEditingController _controller = TextEditingController();

  void _onSubmit(String text) {
    setState(() {
      if (!_inConversation) {
        _inConversation = true;
      }
      _conversation.add(text);
      _conversation.add("Loading..");
      fetchData();
    });
  }

  void _onLLMResponse(String text) {
    setState(() {
      _conversation.removeLast();
      _conversation.add(text);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
          child: !_inConversation
              ? Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    const Text(
                      'What can I help you with?',
                      style: TextStyle(fontSize: 20),
                    ),
                    Container(
                      decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.onPrimary,
                          borderRadius: BorderRadius.circular(12)),
                      margin:
                          EdgeInsets.symmetric(horizontal: 100, vertical: 5),
                      padding: EdgeInsets.fromLTRB(10, 0, 10, 2),
                      child: Row(
                        children: [
                          Expanded(
                              child: TextField(
                            controller: _controller,
                            decoration: InputDecoration(
                              border: InputBorder.none,
                              hintText: "Query your data",
                            ),
                            maxLines: null,
                          )),
                          IconButton(
                              onPressed: () {
                                _onSubmit(_controller.text);
                                _controller.clear();
                              },
                              icon: Icon(Icons.send))
                        ],
                      ),
                    ),
                  ],
                )
              : Stack(children: [
                  ListView.builder(
                      itemCount: _conversation.length,
                      itemBuilder: (context, index) {
                        return ChatMessage(
                            _conversation[index], (index % 2 != 0));
                      }),
                  Positioned(
                    bottom: 20,
                    left: 0,
                    right: 0,
                    child: Container(
                      decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.onPrimary,
                          borderRadius: BorderRadius.circular(12)),
                      margin:
                          EdgeInsets.symmetric(horizontal: 100, vertical: 5),
                      padding: EdgeInsets.fromLTRB(10, 0, 10, 2),
                      child: Row(
                        children: [
                          Expanded(
                              child: TextField(
                            controller: _controller,
                            decoration: InputDecoration(
                              border: InputBorder.none,
                              hintText: "Query your data",
                            ),
                            maxLines: null,
                          )),
                          IconButton(
                              onPressed: () {
                                _onSubmit(_controller.text);
                                _controller.clear();
                              },
                              icon: Icon(Icons.send))
                        ],
                      ),
                    ),
                  )
                ])), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
