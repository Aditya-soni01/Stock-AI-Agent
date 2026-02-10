import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Send, Bot, User, Sparkles, Loader2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { askStockBot, StockBotResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content?: string;
  data?: StockBotResponse["answer"];
  isLoading?: boolean;
}

const initialMessages: Message[] = [
  {
    role: "assistant",
    content:
      "Hello! I'm your AI trading assistant. Ask me about any stock analysis, market conditions, or trading strategies.",
  },
];

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setLoading(true);

    // Add user message
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
    ]);

    // Add loading message
    setMessages((prev) => [
      ...prev,
      { role: "assistant", isLoading: true },
    ]);

    try {
      const response = await askStockBot(userMessage);

      // Replace loading message with actual response
      setMessages((prev) => {
        const newMessages = [...prev];
        const loadingIndex = newMessages.findIndex((m) => m.isLoading);
        if (loadingIndex !== -1) {
          newMessages[loadingIndex] = {
            role: "assistant",
            data: response.answer,
          };
        }
        return newMessages;
      });
    } catch (err) {
      // Replace loading message with error
      setMessages((prev) => {
        const newMessages = [...prev];
        const loadingIndex = newMessages.findIndex((m) => m.isLoading);
        if (loadingIndex !== -1) {
          newMessages[loadingIndex] = {
            role: "assistant",
            content: "Unable to fetch analysis. Please try again.",
          };
        }
        return newMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  const getBiasColor = (bias: string) => {
    const biasLower = bias.toLowerCase();
    if (biasLower.includes("bullish")) return "bg-green-500/20 text-green-400 border-green-500/30";
    if (biasLower.includes("bearish")) return "bg-red-500/20 text-red-400 border-red-500/30";
    if (biasLower.includes("sideways")) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    if (biasLower.includes("cautious")) return "bg-orange-500/20 text-orange-400 border-orange-500/30";
    return "bg-blue-500/20 text-blue-400 border-blue-500/30";
  };

  const getConfidenceColor = (level: string) => {
    const levelLower = level.toLowerCase();
    if (levelLower === "high") return "text-green-400";
    if (levelLower === "medium") return "text-yellow-400";
    return "text-orange-400";
  };

  return (
    <Card className="bg-card border-border flex flex-col h-full">
      <CardHeader className="pb-3 px-4 pt-4">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Sparkles className="h-5 w-5 text-ai-insight" />
          AI Command Panel
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col min-h-0 p-4">
        {/* Messages */}
        <div className="flex-1 space-y-2.5 overflow-y-auto pr-2 mb-3">
          {messages.map((message, index) => (
            <div
              key={`message-${message.role}-${index}`}
              className={`flex gap-2 ${message.role === "user" ? "justify-end" : ""}`}
            >
              {message.role === "assistant" && (
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-ai-insight/20">
                  {message.isLoading ? (
                    <Loader2 className="h-4 w-4 text-ai-insight animate-spin" />
                  ) : (
                    <Bot className="h-4 w-4 text-ai-insight" />
                  )}
                </div>
              )}
              <div
                className={`rounded-lg px-3 py-2 text-sm ${
                  message.role === "user"
                    ? "bg-ai-insight text-white max-w-[70%]"
                    : "bg-secondary text-foreground max-w-[85%]"
                }`}
              >
                {message.isLoading ? (
                  <p className="text-muted-foreground">Analyzing market...</p>
                ) : message.content ? (
                  <p className="leading-relaxed">{message.content}</p>
                ) : message.data ? (
                  <div className="space-y-2">
                    {/* Summary */}
                    <p className="leading-relaxed text-foreground text-sm">
                      {message.data.summary}
                    </p>

                    {/* Market Bias */}
                    <div>
                      <Badge
                        variant="outline"
                        className={`${getBiasColor(message.data.market_bias)} text-xs font-medium`}
                      >
                        {message.data.market_bias}
                      </Badge>
                    </div>

                    {/* Reasoning */}
                    {message.data.reasoning && message.data.reasoning.length > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground">Reasoning:</p>
                        <ul className="list-disc list-inside space-y-0.5 text-xs text-foreground/90 pl-1">
                          {message.data.reasoning.map((point, idx) => (
                            <li key={idx}>{point}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* What to Watch */}
                    {message.data.what_to_watch && message.data.what_to_watch.length > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-muted-foreground">What to Watch:</p>
                        <ul className="list-disc list-inside space-y-0.5 text-xs text-foreground/90 pl-1">
                          {message.data.what_to_watch.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Risk Note */}
                    {message.data.risk_note && (
                      <p className="text-xs text-muted-foreground italic pt-1.5 border-t border-border/50">
                        {message.data.risk_note}
                      </p>
                    )}

                    {/* Confidence Level - at bottom */}
                    <div className="flex items-center gap-1.5 pt-1">
                      <Badge
                        variant="outline"
                        className={`${getConfidenceColor(message.data.confidence_level)} border-current text-xs`}
                      >
                        {message.data.confidence_level}
                      </Badge>
                    </div>
                  </div>
                ) : null}
              </div>
              {message.role === "user" && (
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-muted">
                  <User className="h-4 w-4 text-muted-foreground" />
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick prompts */}
        <div className="mt-2.5 flex flex-wrap gap-1">
          {[
            "What will the market be like today?",
            "Is today good for scalping?",
            "Top picks today",
          ].map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => setInput(prompt)}
              disabled={loading}
              className="rounded-full border border-border bg-secondary px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:border-ai-insight hover:text-ai-insight disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="mt-2.5 flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about any stock or strategy..."
            className="h-9 bg-input border-border text-foreground placeholder:text-muted-foreground text-sm"
            onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
            disabled={loading}
          />
          <Button
            onClick={handleSend}
            size="icon"
            disabled={loading || !input.trim()}
            className="h-9 w-9 shrink-0 rounded-full bg-ai-insight text-white hover:bg-ai-insight/90 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
