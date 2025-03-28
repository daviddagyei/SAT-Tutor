import React, { useState } from 'react';
import { MessageSquare, ThumbsUp, Share2, Flag } from 'lucide-react';

interface Post {
  id: number;
  author: {
    name: string;
    avatar: string;
  };
  content: string;
  likes: number;
  replies: number;
  timestamp: string;
  tags: string[];
}

const samplePosts: Post[] = [
  {
    id: 1,
    author: {
      name: "Sarah Chen",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
    },
    content: "Just scored 1500+ on my practice test! Here are my top study tips...",
    likes: 24,
    replies: 12,
    timestamp: "2h ago",
    tags: ["Study Tips", "Success Story"]
  },
  {
    id: 2,
    author: {
      name: "Alex Thompson",
      avatar: "https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
    },
    content: "Anyone have good resources for mastering the reading section?",
    likes: 15,
    replies: 8,
    timestamp: "5h ago",
    tags: ["Reading", "Help Needed"]
  }
];

export function CommunityForum() {
  const [posts, setPosts] = useState<Post[]>(samplePosts);
  const [newPost, setNewPost] = useState('');

  const handleSubmitPost = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPost.trim()) return;

    const post: Post = {
      id: posts.length + 1,
      author: {
        name: "You",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
      },
      content: newPost,
      likes: 0,
      replies: 0,
      timestamp: "Just now",
      tags: []
    };

    setPosts([post, ...posts]);
    setNewPost('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Community Forum</h2>
        
        <form onSubmit={handleSubmitPost} className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <textarea
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="Share your thoughts, questions, or tips..."
            className="w-full p-4 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            rows={3}
          />
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
            >
              Post
            </button>
          </div>
        </form>

        <div className="space-y-6">
          {posts.map((post) => (
            <div key={post.id} className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-start space-x-4">
                <img
                  src={post.author.avatar}
                  alt={post.author.name}
                  className="w-10 h-10 rounded-full"
                />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{post.author.name}</h3>
                      <p className="text-sm text-gray-500">{post.timestamp}</p>
                    </div>
                    <button className="text-gray-400 hover:text-gray-600">
                      <Flag className="w-5 h-5" />
                    </button>
                  </div>
                  <p className="mt-2 text-gray-800">{post.content}</p>
                  <div className="mt-4 flex items-center space-x-4">
                    <button className="flex items-center space-x-2 text-gray-500 hover:text-indigo-600">
                      <ThumbsUp className="w-5 h-5" />
                      <span>{post.likes}</span>
                    </button>
                    <button className="flex items-center space-x-2 text-gray-500 hover:text-indigo-600">
                      <MessageSquare className="w-5 h-5" />
                      <span>{post.replies}</span>
                    </button>
                    <button className="flex items-center space-x-2 text-gray-500 hover:text-indigo-600">
                      <Share2 className="w-5 h-5" />
                    </button>
                  </div>
                  {post.tags.length > 0 && (
                    <div className="mt-4 flex items-center space-x-2">
                      {post.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}