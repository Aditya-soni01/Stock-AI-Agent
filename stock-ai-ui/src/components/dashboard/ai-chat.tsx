import { Bot, Loader2, Send, Sparkles, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { askStockBot, type StockBotResponse } from "@/lib/api";

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
      "System ready. I can summarize market context from live paper data and explain what to watch next.",
  },
];

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMessage = input.trim();
    setInput("");
    setLoading(true);

    setMessages((prev) => [...prev, { role: "user", content: userMessage }, { role: "assistant", isLoading: true }]);

    try {
      const response = await askStockBot(userMessage);
      setMessages((prev) => {
        const next = [...prev];
        const loadingIndex = next.findIndex((message) => message.isLoading);
        if (loadingIndex !== -1) next[loadingIndex] = { role: "assistant", data: response.answer };
        return next;
      });
    } catch {
      setMessages((prev) => {
        const next = [...prev];
        const loadingIndex = next.findIndex((message) => message.isLoading);
        if (loadingIndex !== -1) next[loadingIndex] = { role: "assistant", content: "Unable to fetch analysis. Please try again." };
        return next;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="glass-card glass-card-hover flex min-h-[260px] flex-col p-5">
      <h3 className="mb-3 flex items-center gap-2 text-2xl font-medium text-white">
        <Sparkles className="h-4 w-4 text-[#00ff88]" />
        AI Command
      </h3>

      <div className="mb-3 flex-1 space-y-2 overflow-y-auto pr-1">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`flex gap-2 ${message.role === "user" ? "justify-end" : ""}`}>
            {message.role === "assistant" && (
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#0d1a0d]">
                {message.isLoading ? <Loader2 className="h-4 w-4 animate-spin text-[#00ff88]" /> : <Bot className="h-4 w-4 text-[#00ff88]" />}
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-xl border px-3 py-2 text-sm ${
                message.role === "user" ? "border-[#00ff88]/30 bg-[#00ff88]/15 text-[#d9ffe8]" : "border-[#1a2e1a] bg-[#0a140a] text-white"
              }`}
            >
              {message.isLoading && <p className="text-[#8fa98f]">Analyzing...</p>}
              {!message.isLoading && message.content && <p>{message.content}</p>}
              {!message.isLoading && message.data && (
                <div className="space-y-2">
                  <p>{message.data.summary}</p>
                  <Badge variant="outline" className="border-[#1a2e1a] text-[#8fa98f]">
                    {message.data.market_bias} | {message.data.confidence_level}
                  </Badge>
                  {message.data.reasoning?.length > 0 && (
                    <ul className="list-disc space-y-1 pl-5 text-xs text-[#8fa98f]">
                      {message.data.reasoning.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>

            {message.role === "user" && (
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#162316]">
                <User className="h-4 w-4 text-[#8fa98f]" />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="mt-auto flex gap-2">
        <Input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask AI terminal..."
          className="h-10 rounded-xl border-[#1a2e1a] bg-[#050b05] text-white placeholder:text-[#6f876f] focus-visible:border-[#00ff88] focus-visible:ring-0"
          onKeyDown={(event) => event.key === "Enter" && !loading && handleSend()}
          disabled={loading}
        />
        <Button
          onClick={handleSend}
          size="icon"
          disabled={loading || !input.trim()}
          className="h-10 w-10 rounded-full bg-[#00ff88] text-black hover:bg-[#00e97c]"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </div>
    </section>
  );
}
