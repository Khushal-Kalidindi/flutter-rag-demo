// ignore_for_file: prefer_const_constructors

import 'package:flutter/material.dart';

class ChatMessage extends StatelessWidget {
  final String _text;
  final bool isLLM;
  const ChatMessage(this._text, this.isLLM);
  @override
  Widget build(BuildContext context) {
    return Container(
        alignment: isLLM ? Alignment.bottomLeft : Alignment.bottomRight,
        child: Container(
          decoration: BoxDecoration(
              color: !isLLM
                  ? Theme.of(context).colorScheme.onPrimary
                  : Theme.of(context).colorScheme.onSecondary,
              borderRadius: BorderRadius.circular(16)),
          margin: EdgeInsets.symmetric(horizontal: 100, vertical: 5),
          padding: EdgeInsets.fromLTRB(10, 10, 10, 10),
          child: Text(_text),
        ));
  }
}
