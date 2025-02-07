// ignore_for_file: prefer_const_constructors, prefer_const_literals_to_create_immutables

import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'chat_message.dart';
import 'openai.dart';
import 'pinecone.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key, required this.title});

  final String title;

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  bool _inConversation = false;
  final _conversation = <String>[];
  late Future<String> _futureData;
  String _data = "";

  Future<void> fetchData(String query) async {
    List<double> embedding_res =
        await OpenAIService().generateEmbeddings(query);
    Map<String, dynamic> pinecone_res = await PineconeService()
        .queryIndex(dotenv.env["PINECONE_INDEX"]!, embedding_res);
    String context = pinecone_res['matches'][0]['metadata']['text'];
    String LLM_res = await OpenAIService().generateLLMResponse(query, context);
    _onLLMResponse(LLM_res);
  }

  final TextEditingController _controller = TextEditingController();

  void _onSubmit(String text) {
    setState(() {
      if (!_inConversation) {
        _inConversation = true;
      }
      _conversation.add(text);
      _conversation.add("Loading..");
      fetchData(text);
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
