import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

class OpenAIService {
  final String apiKey = dotenv.env['OPENAI_API_KEY'] ?? "";
  static const String apiUrl = "https://api.openai.com/v1/chat/completions";

  Future<String> generateLLMResponse(
      String query, List<Map<String, String>> context) async {
    String contextString = context.map((doc) => doc['text'] ?? "").join(" ");

    String promptTemplate = '''
  Context: $contextString
  Question: $query
  If this context contains information that can answer the question, give a better and summarized answer. 
  Else say "I don't have enough info to answer."
      ''';

    var requestBody = {
      "model": "gpt-4",
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": promptTemplate}
      ],
      "temperature": 0
    };

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $apiKey"
        },
        body: jsonEncode(requestBody),
      );

      if (response.statusCode == 200) {
        var responseBody = jsonDecode(response.body);
        return responseBody['choices'][0]['message']['content'] ??
            "No response";
      } else {
        return "Error: ${response.body}";
      }
    } catch (e) {
      return "Error generating LLM response: $e";
    }
  }
}
