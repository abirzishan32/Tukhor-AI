'use client';

import { ChatPage } from '@/components/chat/ChatPage';
import { useParams } from 'next/navigation';
import { Suspense } from 'react';

export default function ChatDetailPage() {
  const params = useParams();
  const chatId = params?.chatId as string;

  return  (
    <Suspense fallback={<div>Loading chat...</div>}>
        <ChatPage chatId={chatId} />
    </Suspense>
  );
}