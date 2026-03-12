        report = generator.generate_report(
            exchange=args.exchange,
            date=date_obj,
            data=data,
            rag_provider=rag_provider
        )
        
        # Save report