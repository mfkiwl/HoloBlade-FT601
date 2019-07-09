
// Authors: A. Kadis
// Date:    9th July 2019

// PC_TX Encapsulates to functionality to send UART data to a FTDI USB2 Chip
// It handles sending data through a FIFO and over a UART to a PC
// Encapsualtes and manages a UART_TX_DRIVER and a UART_TX_FIFO

// TODO: Add decent reset functionality to all the sub-blocks by linking up o_reset_all appropriately


module PC_TX(

	// Control Signals
	input i_clock,

	// DataRouter Side
	input[31:0] i_fifo_word_data,        // Data from Uart
	input       i_serial_next_word_cmd,  // New byte from Uart Received signal
	output      o_tx_active,             // Use the active signal to drive the DataRouter sending more data TODO: Hack atm, upgrade with a FIFO

	// PC Side
   output o_UART_TX                     // Output line for UART

   );
	

	
	
	
	
//////////////////////////
////// Serialiser ////////
//////////////////////////

// Interfacing signals for Serialiser
wire send_next_byte_cmd;
// Byte to output from UART - controlled by the Serialiser
wire[7:0] tx_byte_output;
// Serialiser handles transforming our 4-byte word into a stream of single bytes
 SERIALISER serialiser(

	// Control Signals
	.i_clock(i_clock),
	
	// Input-Side
	.i_fifo_word_data(i_fifo_word_data),                   // Data from Uart
	.i_serial_next_word_cmd(i_serial_next_word_cmd),       // New byte from Uart Received signal
	.i_tx_byte_complete(tx_done),                          // Byte has been successfully Tx'd
	
	// Output-Side
	.o_send_next_byte_cmd(send_next_byte_cmd),             // Flag to indicate whether or not the serialisation Unit is busy
   .o_serial_data_byte(tx_byte_output),                   // Data Output for FIFO
   .o_serial_is_busy_sig(serial_is_busy_sig),             // Signal to indicate that serialse is complete
	  
 );	
	
	
	
//////////////////////////
//////// Uart TX /////////
//////////////////////////

// Interfacing signals for uart_tx
//wire tx_active;
wire tx_done;
// Want to interface to 115200 baud UART with our 50 MHz clock
// 50000000 / 115200 = 435 Clocks Per Bit.
parameter c_CLKS_PER_BIT    = 435;
// Module to control uart to pc
uart_tx #(.CLKS_PER_BIT(c_CLKS_PER_BIT)) pc_tx(

	.i_Clock(i_clock),              // Clock
   .i_Tx_DV(send_next_byte_cmd),   // Command to start TX of individual Byte
   .i_Tx_Byte(tx_byte_output),     // Byte of data to send
   .o_Tx_Active(o_tx_active),      // Flag for whether or not UART is active
   .o_Tx_Serial(o_UART_TX),        // Output line for UART
   .o_Tx_Done(tx_done)             // Flag which is high for 1 cycle after Tx Complete
	  
 );

 endmodule
