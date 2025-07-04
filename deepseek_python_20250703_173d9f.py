class ErrorHandler:
    @staticmethod
    async def handle_error(error, context=None):
        error_type = type(error).__name__
        
        if error_type == 'ConnectionError':
            await ErrorHandler.handle_connection_error(error, context)
        elif 'margin' in str(error).lower():
            await ErrorHandler.handle_margin_error(error, context)
        elif 'slippage' in str(error).lower():
            await ErrorHandler.handle_slippage_error(error, context)
        else:
            logging.error(f"Unhandled error: {str(error)}")
            await asyncio.sleep(10)  # Prevent tight error loops

    @staticmethod
    async def handle_connection_error(error, context):
        logging.error(f"Connection error: {str(error)}")
        if context and hasattr(context, 'reconnect'):
            await context.reconnect()
        else:
            await asyncio.sleep(30)  # Wait before retrying

    @staticmethod
    async def handle_margin_error(error, context):
        logging.error("Margin error - insufficient funds")
        if context and hasattr(context, 'adjust_lot_size'):
            new_lot = context.lot_size * 0.5  # Reduce lot size by half
            if new_lot >= context.min_lot:
                context.lot_size = new_lot
                logging.warning(f"Reduced lot size to {new_lot}")
            else:
                logging.error("Lot size below minimum - cannot execute trade")
        else:
            await asyncio.sleep(60)  # Wait before checking again

    @staticmethod
    async def handle_slippage_error(error, context):
        logging.warning("Slippage detected - adjusting order")
        if context and hasattr(context, 'adjust_for_slippage'):
            await context.adjust_for_slippage()
        else:
            await asyncio.sleep(5)  # Brief pause before retry