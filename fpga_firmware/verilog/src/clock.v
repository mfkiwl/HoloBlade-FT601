
// This file takes the 24MHz clock input and passes it through a PLL to output 50.25 MHz
// It then buffers the output so it doesn't sag
module clock(
   input        i_xtal,
   output       o_sys_clk
);

// Raw output from PLL - we'll buffer it before outputting
wire pll_clk_unbuf;





/////////////////////////////////////////////////////////////////////////
///////// MAKE SURE YOU UPDATE THE UART AND SPI TIMINGS WHEN UPDATING !!!
/////////////////////////////////////////////////////////////////////////
// TODO: Make this programmatic

/////////////////////////////////////////////////////////
//////////////////// 100 MHz Option /////////////////////
/////////////////////////////////////////////////////////
// Drive our system off a 100 MHz Clock
// Note that due to PLL limitations, its actually 100.5HMz
// These values were originally obtained from the 'configure PLL option of iCEcube2 GUI'
// SB_PLL40_CORE #(.FEEDBACK_PATH("SIMPLE"),
// 	   .PLLOUT_SELECT("GENCLK"),
//                 .DIVR(4'b0001),
//                 .DIVF(7'b1000010),
//                 .DIVQ(3'b011),
//                 .FILTER_RANGE(3'b001)
// ) pll_config (
//                 .REFERENCECLK(i_xtal),
//                 .PLLOUTGLOBAL(pll_clk_unbuf),
//                 .LOCK(),
//                 .RESETB(1'b1),
//                 .BYPASS(1'b0)
// );


/////////////////////////////////////////////////////////
/////////////////// 62.5 MHz Option /////////////////////
/////////////////////////////////////////////////////////
// Temp mod so use 62.25 MHz instead, slower is easier for development (also get good sampling on the saleae as is 1/4th of the sampling frequency)
// These values were originally obtained from the 'configure PLL option of iCEcube2 GUI'
SB_PLL40_CORE #(.FEEDBACK_PATH("SIMPLE"),
	   .PLLOUT_SELECT("GENCLK"),
                .DIVR(4'b0001),
                .DIVF(7'b1010010),
                .DIVQ(3'b100),
                .FILTER_RANGE(3'b001)
) pll_config (
                .REFERENCECLK(i_xtal),
                .PLLOUTGLOBAL(pll_clk_unbuf),
                .LOCK(),
                .RESETB(1'b1),
                .BYPASS(1'b0)
);

// /////////////////////////////////////////////////////////
// /////////////////// 66.0 MHz Option /////////////////////
// /////////////////////////////////////////////////////////
// // Temp mod so use 66.0 MHz instead, slower is easier for development and these values suit the USB3 FIFO Chip
// // These values were originally obtained from the 'configure PLL option of iCEcube2 GUI'
// // Matches FIFO speed too
// SB_PLL40_CORE #(.FEEDBACK_PATH("SIMPLE"),
// 	   .PLLOUT_SELECT("GENCLK"),
//                 .DIVR(4'b0000),
//                 .DIVF(7'b0101011),
//                 .DIVQ(3'b100),
//                 .FILTER_RANGE(3'b010)
// ) pll_config (
//                 .REFERENCECLK(i_xtal),
//                 .PLLOUTGLOBAL(pll_clk_unbuf),
//                 .LOCK(),
//                 .RESETB(1'b1),
//                 .BYPASS(1'b0)
// );

// Buffer the output so it doesn't sag
SB_GB clk_gb ( .USER_SIGNAL_TO_GLOBAL_BUFFER(pll_clk_unbuf), .GLOBAL_BUFFER_OUTPUT(o_sys_clk) );

endmodule