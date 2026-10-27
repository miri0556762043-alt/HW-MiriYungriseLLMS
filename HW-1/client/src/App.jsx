import { useState, useEffect, useRef } from 'react';
import './App.css';
import ReactMarkdown from 'react-markdown';
function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    const updatedMessages = [
      ...messages,
      { role: 'user', content: userMessage }
    ];

    setMessages(updatedMessages);
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: updatedMessages
        }),
      });

      if (!response.ok) {
        throw new Error('שגיאה בתקשורת מול השרת');
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.output_text }
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'מצטערים, לא הצלחנו להתחבר לשרת. נסי שוב בעוד רגע.'
        }
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="chat-page" dir="rtl">
      <main className="chat-card">
        <header className="chat-header">
          <div className="assistant-avatar">✦</div>

          <div className="header-text">
            <h1>העוזר החכם שלי</h1>
            <p>
              <span className="status-dot"></span>
              כאן בשבילך, בכל שאלה
            </p>
          </div>

          <button
            className="header-action"
            type="button"
            title="צ'אט חכם"
            aria-label="מידע על הצ'אט"
          >
            ✧
          </button>
        </header>

        <section
          className="messages-area"
          aria-label="הודעות הצ'אט"
          aria-live="polite"
        >
          {messages.length === 0 && (
            <div className="welcome-screen">
              <div className="welcome-icon">✦</div>
              <h2>שלום! איך אפשר לעזור?</h2>
              <p>
                אפשר לשאול אותי שאלות, לבקש הסברים
                או להתחיל שיחה חדשה.
              </p>

              <div className="suggestions">
                <button
                  type="button"
                  onClick={() => setInput('תסביר לי איך המערכת עובדת')}
                >
                  הסבר על המערכת <span>←</span>
                </button>

                <button
                  type="button"
                  onClick={() => setInput('עזור לי להתחיל')}
                >
                  בוא נתחיל <span>←</span>
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message-row ${
                msg.role === 'user' ? 'user-row' : 'assistant-row'
              }`}
            >
              {msg.role !== 'user' && (
                <div className="message-avatar bot-avatar">✦</div>
              )}

              <div className="message-content">
                <div className={`message-bubble ${
                  msg.role === 'user' ? 'user-bubble' : 'bot-bubble'
                }`}>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
                <span className="message-label">
                  {msg.role === 'user' ? 'את/ה' : 'העוזר החכם'}
                </span>
              </div>

              {msg.role === 'user' && (
                <div className="message-avatar user-avatar">א</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="message-row assistant-row">
              <div className="message-avatar bot-avatar">✦</div>
              <div className="message-content">
                <div className="message-bubble bot-bubble typing-bubble">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="message-label">מנסח תשובה...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </section>

        <form className="composer" onSubmit={sendMessage}>
          <div className="composer-inner">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (
                  e.key === 'Enter' &&
                  !e.shiftKey &&
                  !e.nativeEvent.isComposing
                ) {
                  e.preventDefault();
                  e.currentTarget.form.requestSubmit();
                }
              }}
              placeholder="כתבו כאן הודעה..."
              aria-label="כתיבת הודעה"
              rows={1}
              disabled={loading}
            />

            <button
              type="submit"
              className="send-button"
              disabled={!input.trim() || loading}
              aria-label="שליחת הודעה"
              title="שליחה"
            >
              <svg
                viewBox="0 0 24 24"
                width="23"
                height="23"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M22 2 11 13" />
                <path d="m22 2-7 20-4-9-9-4Z" />
              </svg>
            </button>
          </div>

          <p className="composer-note">
            לחיצה על Enter לשליחה · Shift + Enter לשורה חדשה
          </p>
        </form>
      </main>
    </div>
  );
}

export default App;