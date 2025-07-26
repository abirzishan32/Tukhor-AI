#!/usr/bin/env python3
"""
Quick Start Script for তুখোড় RAG System
This script helps you get the RAG system up and running quickly
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def quick_start():
    """Quick start the RAG system"""
    print("🚀 তুখোড় RAG System - Quick Start")
    print("=" * 50)

    try:
        # Step 1: Check dependencies
        print("1️⃣ Checking dependencies...")

        missing_deps = []
        try:
            import sentence_transformers

            print("   ✅ sentence-transformers")
        except ImportError:
            missing_deps.append("sentence-transformers")

        try:
            import google.generativeai

            print("   ✅ google-generativeai")
        except ImportError:
            missing_deps.append("google-generativeai")

        try:
            import fitz  # PyMuPDF

            print("   ✅ PyMuPDF")
        except ImportError:
            missing_deps.append("PyMuPDF")

        try:
            from prisma import Prisma

            print("   ✅ prisma")
        except ImportError:
            missing_deps.append("prisma")

        if missing_deps:
            print(f"   ❌ Missing dependencies: {', '.join(missing_deps)}")
            print("   Please install them with: pip install -r requirements.txt")
            return False

        # Step 2: Check environment variables
        print("\n2️⃣ Checking environment configuration...")

        from config.settings import settings

        required_vars = ["GOOGLE_API_KEY", "DATABASE_URL"]
        missing_vars = []

        for var in required_vars:
            if hasattr(settings, var) and getattr(settings, var):
                print(f"   ✅ {var}")
            else:
                missing_vars.append(var)
                print(f"   ❌ {var}")

        if missing_vars:
            print(f"   Missing environment variables: {', '.join(missing_vars)}")
            print("   Please check your .env file")
            return False

        # Step 3: Test database connection
        print("\n3️⃣ Testing database connection...")

        try:
            async with Prisma() as db:
                await db.query_raw("SELECT 1")
            print("   ✅ Database connection successful")
        except Exception as e:
            print(f"   ❌ Database connection failed: {str(e)}")
            return False

        # Step 4: Initialize embedding service
        print("\n4️⃣ Initializing embedding service...")

        try:
            from services.embedding_service import EmbeddingService

            embedding_service = EmbeddingService()
            test_embedding = await embedding_service.encode_text_async("test")
            print(f"   ✅ Embedding service ready (dimension: {len(test_embedding)})")
        except Exception as e:
            print(f"   ❌ Embedding service failed: {str(e)}")
            return False

        # Step 5: Initialize knowledge base
        print("\n5️⃣ Initializing knowledge base...")

        try:
            from services.document_service import DocumentService

            document_service = DocumentService()

            result = await document_service.initialize_knowledge_base()
            print(f"   ✅ Knowledge base: {result['status']}")
            print(f"   📊 Document chunks: {result['chunk_count']}")

        except Exception as e:
            print(f"   ❌ Knowledge base initialization failed: {str(e)}")
            print("   This might be due to network issues downloading the PDF")
            print("   You can manually upload documents later")

        # Step 6: Test RAG pipeline
        print("\n6️⃣ Testing RAG pipeline...")

        try:
            from services.rag_service import RAGService

            rag_service = RAGService()

            test_question = "What is this document about?"
            result = await rag_service.generate_answer(test_question)

            print(f"   ✅ RAG pipeline working")
            print(f"   📝 Test response: {result['answer'][:100]}...")
            print(f"   ⚡ Response time: {result['response_time']:.2f}s")
            print(f"   🎯 Confidence: {result['confidence']:.3f}")

        except Exception as e:
            print(f"   ❌ RAG pipeline test failed: {str(e)}")
            return False

        # Step 7: Bengali test
        print("\n7️⃣ Testing Bengali capabilities...")

        try:
            bengali_question = "এই ডকুমেন্ট সম্পর্কে বলুন"
            result = await rag_service.generate_answer(bengali_question)

            print(f"   ✅ Bengali processing working")
            print(f"   📝 Bengali response: {result['answer'][:100]}...")
            print(f"   🌐 Detected language: {result['language']}")

        except Exception as e:
            print(f"   ⚠️ Bengali test warning: {str(e)}")
            print("   Basic system works, but Bengali processing may need attention")

        print("\n" + "=" * 50)
        print("🎉 Quick Start Complete!")
        print("=" * 50)

        print("\n📋 Next Steps:")
        print("1. Start the server: python start_server.py")
        print("2. Test the API: python advanced_cli_test.py --mode interactive")
        print("3. Run comprehensive tests: python advanced_cli_test.py --mode all")
        print("4. Access API docs: http://localhost:8000/docs")

        print("\n🔗 Available Endpoints:")
        print("- POST /api/v1/rag/ask - Ask questions")
        print("- GET /api/v1/system/status - System status")
        print("- POST /api/v1/documents/upload - Upload documents")

        return True

    except Exception as e:
        print(f"\n❌ Critical error during quick start: {str(e)}")
        return False


async def test_specific_queries():
    """Test the specific queries from requirements"""
    print("\n🧪 Testing Specific Bengali Queries")
    print("=" * 50)

    test_cases = [
        "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?",
        "কাকে অনুপমের ভাগ্য দেবতা বলে উল্লেখ করা হয়েছে?",
        "বিয়ের সময় কল্যাণীর প্রকৃত বয়স কত ছিল?",
    ]

    try:
        from services.rag_service import RAGService

        rag_service = RAGService()

        for i, question in enumerate(test_cases, 1):
            print(f"\n{i}. Question: {question}")

            result = await rag_service.generate_answer(question)

            print(f"   Answer: {result['answer']}")
            print(f"   Confidence: {result['confidence']:.3f}")
            print(f"   Sources: {result['chunks_retrieved']}")
            print(f"   Language: {result['language']}")

    except Exception as e:
        print(f"❌ Error testing specific queries: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="তুখোড় RAG Quick Start")
    parser.add_argument(
        "--test-queries", action="store_true", help="Test specific Bengali queries"
    )

    args = parser.parse_args()

    try:
        if args.test_queries:
            asyncio.run(test_specific_queries())
        else:
            success = asyncio.run(quick_start())

            if success:
                print("\n✨ System is ready! You can now start using the RAG system.")
            else:
                print("\n💥 Quick start failed. Please check the errors above.")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 Quick start cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
