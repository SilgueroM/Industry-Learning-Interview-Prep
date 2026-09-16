import sys
import io
import traceback
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QSplitter, 
                             QTextEdit, QTextBrowser, QPushButton, QLabel, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette

# ==============================================================================
# EXPANDED 50-QUESTION BANK & GRADING DATA
# ==============================================================================
DATA = {
    "Module 1: EM & IR Drop Fundamentals": [
        {
            "id": "EMIR_01", "type": "theory", "title": "Static vs. Dynamic IR Drop",
            "question": "Explain the physical difference between static IR drop and dynamic IR drop. Which one requires vector-driven (VCD) switching activity to analyze?",
            "keywords": ["static", "dc", "average", "dynamic", "transient", "spike", "switching", "vcd"],
            "answer": "Static IR drop is the steady-state DC voltage drop caused by constant average current flowing through the resistive power grid (V = I*R). Dynamic IR drop is transient voltage droop caused by peak current spikes (L*di/dt and R*I) when many logic gates switch simultaneously. Dynamic IR requires vector-driven (VCD/FSDB) switching activity."
        },
        {
            "id": "EMIR_02", "type": "theory", "title": "Analog Sensitivity to Local IR Drop",
            "question": "Why is local IR drop significantly more dangerous for an analog differential amplifier than a global IR drop across the entire block?",
            "keywords": ["mismatch", "offset", "cmrr", "symmetric", "differential", "bias"],
            "answer": "Analog circuits depend on symmetric matching. A global IR drop affects both sides equally, preserving balance. A local IR drop creates a localized voltage gradient, causing one transistor to operate at a different bias level. This introduces DC offset errors and degrades CMRR."
        },
        {
            "id": "EMIR_03", "type": "theory", "title": "Electromigration (EM) Mechanism",
            "question": "Describe the physical mechanism of Electromigration. What structural defects form when current density is excessively high?",
            "keywords": ["momentum", "electron", "wind", "ions", "lattice", "void", "hillock", "density"],
            "answer": "EM occurs when high current density causes moving electrons to transfer momentum to metal lattice ions ('electron wind'). Over time, metal atoms migrate in the direction of electron flow, resulting in 'voids' (open circuits) and 'hillocks' (short circuits)."
        },
        {
            "id": "EMIR_04", "type": "theory", "title": "Current Crowding",
            "question": "Define current crowding. At what specific geometric layout features does this most commonly occur?",
            "keywords": ["corners", "bends", "90-degree", "vias", "localized", "density", "uneven"],
            "answer": "Current crowding occurs when electrons do not spread evenly across a conductor, creating localized hotspots of extreme current density. This most commonly happens at 90-degree layout bends, inner corners, or when a wide metal trace transitions abruptly into a narrow via array."
        },
        {
            "id": "EMIR_05", "type": "theory", "title": "Role of Decoupling Capacitors",
            "question": "What role do on-chip decoupling capacitors (decaps) play in the power delivery network (PDN), and how do they mitigate dynamic voltage droop?",
            "keywords": ["charge", "reservoir", "transient", "spikes", "dynamic", "local", "droop"],
            "answer": "Decaps act as local charge reservoirs. During high switching activity, they supply instantaneous transient current to logic gates much faster than the distant main power supply can, flattening out current spikes and mitigating dynamic IR droop."
        },
        {
            "id": "EMIR_06", "type": "theory", "title": "Advanced Nodes EM/IR",
            "question": "Why do EM and IR drop become exponentially worse at advanced process nodes (e.g., 5nm or 3nm FinFET) compared to older planar nodes?",
            "keywords": ["shrink", "cross-sectional", "area", "resistance", "density", "current"],
            "answer": "As nodes shrink, the cross-sectional area of metal interconnects decreases, significantly increasing both wire resistance (worsening IR drop) and current density (worsening EM). Furthermore, FinFETs have higher drive current per footprint, concentrating more power in smaller areas."
        },
        {
            "id": "EMIR_07", "type": "theory", "title": "Redundant Vias",
            "question": "How does deploying a redundant via array (via ladder) between metal layers mitigate local IR drop?",
            "keywords": ["parallel", "resistance", "divide", "current", "bottleneck"],
            "answer": "Vias have inherent resistance and act as current bottlenecks. Placing an array of redundant vias in parallel divides the total current among them and drastically reduces the total contact resistance between the metal layers, lowering the local IR drop."
        },
        {
            "id": "EMIR_08", "type": "theory", "title": "Black's Equation",
            "question": "According to Black's Equation, how does local temperature (Joule heating) impact the Mean Time to Failure (MTTF) of a metal interconnect?",
            "keywords": ["temperature", "exponentially", "decreases", "activation", "energy", "heat"],
            "answer": "According to Black's Equation, MTTF is exponentially dependent on temperature. An increase in local temperature (Joule heating) dramatically accelerates atomic diffusion, exponentially decreasing the lifespan (MTTF) of the metal interconnect before EM failure."
        },
        {
            "id": "EMIR_09", "type": "theory", "title": "EM/IR Feedback Loop",
            "question": "Explain the vicious cycle (feedback loop) between EM and IR Drop.",
            "keywords": ["void", "resistance", "temperature", "heat", "accelerates", "worse"],
            "answer": "High current causes EM, which forms a void. The void reduces the wire's cross-sectional area, increasing its local resistance. Higher resistance causes a localized IR drop and generates more Joule heating. The increased temperature exponentially accelerates further EM, creating a destructive feedback loop."
        },
        {
            "id": "EMIR_10", "type": "theory", "title": "AC vs. DC EM Limits",
            "question": "Why do bidirectional signal nets (AC) have different (often higher) EM current limits compared to unidirectional (DC) power/ground nets?",
            "keywords": ["recovery", "alternating", "direction", "heal", "push", "back", "unidirectional"],
            "answer": "In DC power nets, electrons always flow in one direction, causing continuous atomic migration. In AC signal nets, the current direction alternates. Atoms pushed in one direction during the rising edge are partially pushed back during the falling edge (EM recovery/healing effect), allowing for higher peak current limits."
        },
        {
            "id": "EMIR_11", "type": "theory", "title": "Sheet Resistance Calculation",
            "question": "If you have the sheet resistance (Rs) of a metal layer, how do you calculate the total resistance of a routed trace given its length (L) and width (W)?",
            "keywords": ["squares", "length", "width", "multiply", "ratio"],
            "answer": "Total resistance is calculated by multiplying the sheet resistance by the number of 'squares' in the trace. The formula is R = Rs * (L / W)."
        },
        {
            "id": "EMIR_12", "type": "theory", "title": "Macro Placement",
            "question": "How does the density and placement of power-hungry macros (like SRAM) dictate localized IR drop?",
            "keywords": ["concentrates", "current", "draw", "center", "distance", "pads"],
            "answer": "Placing high-density, power-hungry macros near the center of the chip or clustered together concentrates massive current draw in one area. This forces current to travel over long resistive distances from the power pads, creating severe localized IR drop hotspots."
        },
        {
            "id": "EMIR_13", "type": "theory", "title": "Signoff Tools vs PEX",
            "question": "In an industry flow, what role do tools like Cadence Voltus or Synopsys RedHawk play compared to standard parasitic extraction (PEX)?",
            "keywords": ["power", "integrity", "maps", "voltage", "drop", "simulate", "extraction", "rc"],
            "answer": "Standard PEX (like Calibre) only extracts the RC parasitics of the physical layout. Voltus and RedHawk are Power Integrity signoff tools; they take those PEX parasitics, combine them with switching activity, and simulate the entire power grid to generate dynamic IR drop maps and EM violation reports."
        },
        {
            "id": "EMIR_14", "type": "theory", "title": "Fixing EM on Signal Nets",
            "question": "If a signal net violates EM constraints, what are two layout-level modifications you can make to fix it without changing the standard cell drive strength?",
            "keywords": ["widen", "width", "parallel", "layer", "thicker", "vias"],
            "answer": "1) Widen the metal trace to increase cross-sectional area and reduce current density. 2) Route the net to a higher, thicker metal layer (which naturally has higher EM limits). 3) Add parallel redundant routing."
        },
        {
            "id": "EMIR_15", "type": "theory", "title": "Power Rings and Straps",
            "question": "Describe how a hierarchical power grid (using power rings and orthogonal straps) distributes current.",
            "keywords": ["mesh", "orthogonal", "top", "thick", "lower", "standard", "cells"],
            "answer": "A hierarchical grid uses ultra-thick metal layers at the top for low-resistance global routing. Current flows from the package pads into massive power rings, then down through an orthogonal mesh of power straps (M4/M5), eventually stepping down through via arrays to the thin M1 rails that directly power the standard cells."
        }
    ],
    "Module 2: VLSI & Mixed-Signal Concepts": [
        {
            "id": "VLSI_01", "type": "theory", "title": "CMOS Transistor Sizing",
            "question": "In standard CMOS inverter design, why is the PMOS transistor typically sized 2 to 3 times wider than the NMOS?",
            "keywords": ["mobility", "electron", "hole", "resistance", "symmetric", "rise", "fall"],
            "answer": "Electron mobility is 2 to 3 times higher than hole mobility. PMOS must be made wider than the NMOS to achieve equal on-resistance, ensuring symmetrical rise/fall times."
        },
        {
            "id": "VLSI_02", "type": "theory", "title": "Comparator Hysteresis",
            "question": "When designing an analog comparator, what is the purpose of adding positive feedback (hysteresis)?",
            "keywords": ["noise", "margin", "chatter", "oscillations", "thresholds", "positive"],
            "answer": "Hysteresis uses positive feedback to create two different threshold voltages for low-to-high and high-to-low transitions, preventing rapid oscillation ('chatter') from noisy inputs."
        },
        {
            "id": "VLSI_03", "type": "theory", "title": "RC Delay",
            "question": "Write the formula for an RC time constant. How do interconnect resistance and capacitance impact signal propagation delay?",
            "keywords": ["tau", "r", "c", "quadratic", "length", "degradation"],
            "answer": "Tau = R * C. Wire delay scales quadratically with length (Elmore delay) because both total resistance and total capacitance increase linearly. High RC degrades edge rates and increases propagation delay."
        },
        {
            "id": "VLSI_04", "type": "theory", "title": "NAND Gate Topology",
            "question": "Describe the schematic topology of a 2-input CMOS NAND gate.",
            "keywords": ["pmos", "parallel", "nmos", "series", "vdd", "gnd"],
            "answer": "A 2-input NAND has two PMOS transistors in parallel connected to VDD, and two NMOS transistors in series connected to Ground. The output is taken between the PMOS and NMOS networks."
        },
        {
            "id": "VLSI_05", "type": "theory", "title": "MOSFET Operating Regions",
            "question": "For an NMOS transistor operating as an analog amplifier, in what region must it be biased, and why?",
            "keywords": ["saturation", "active", "constant", "current", "source", "gain", "linear"],
            "answer": "It must be biased in the saturation region (active region). In saturation, the transistor acts as a voltage-controlled current source with high output resistance, which is necessary to achieve high intrinsic voltage gain."
        },
        {
            "id": "VLSI_06", "type": "theory", "title": "Body Effect",
            "question": "How does the body effect alter the threshold voltage (Vth) of a transistor?",
            "keywords": ["source", "bulk", "voltage", "difference", "increases", "threshold"],
            "answer": "The body effect occurs when the bulk (substrate) is not tied to the same potential as the source (Vsb > 0). This increases the depletion region width, which consequently increases the threshold voltage (Vth) required to turn the transistor on."
        },
        {
            "id": "VLSI_07", "type": "theory", "title": "Dynamic Power Formula",
            "question": "What is the formula for dynamic power dissipation in a CMOS circuit? Define the terms.",
            "keywords": ["p", "alpha", "c", "v", "f", "frequency", "capacitance", "voltage", "activity"],
            "answer": "P = alpha * C * V^2 * f. Alpha is the activity factor (probability of switching), C is the total load capacitance, V is the supply voltage, and f is the clock frequency."
        },
        {
            "id": "VLSI_08", "type": "theory", "title": "Leakage Power",
            "question": "Name two primary sources of static power (leakage current) in modern semiconductor devices.",
            "keywords": ["subthreshold", "gate", "oxide", "tunneling", "junction", "reverse", "bias"],
            "answer": "1) Subthreshold leakage (current flowing from drain to source even when Vgs < Vth). 2) Gate oxide tunneling leakage (electrons quantum-tunneling through ultra-thin gate dielectrics). 3) Reverse-biased PN junction leakage."
        },
        {
            "id": "VLSI_09", "type": "theory", "title": "CMOS Latch-up",
            "question": "Describe the physical mechanism behind CMOS latch-up and how it is prevented.",
            "keywords": ["parasitic", "bjt", "thyristor", "short", "vdd", "gnd", "guard", "rings"],
            "answer": "Latch-up is the inadvertent creation of a low-impedance path between VDD and GND caused by parasitic cross-coupled PNPN bipolar transistors acting like a thyristor. It is prevented by using substrate guard rings and tap cells to keep the local substrate/well tied firmly to VDD/GND."
        },
        {
            "id": "VLSI_10", "type": "theory", "title": "Small vs Large Signal",
            "question": "Briefly explain the difference between small-signal modeling and large-signal operation in IC design.",
            "keywords": ["linear", "operating", "point", "dc", "bias", "ac", "non-linear", "swing"],
            "answer": "Large-signal operation describes the non-linear, full-swing DC behavior of a circuit (e.g., a logic gate switching 0 to VDD). Small-signal modeling linearizes the circuit around a specific DC operating point to easily analyze AC parameters like gain and bandwidth."
        }
    ],
    "Module 3: Digital Design & Timing": [
        {
            "id": "DIG_01", "type": "theory", "title": "Setup & Hold Definitions",
            "question": "Define setup time and hold time for a flip-flop. What happens if either is violated?",
            "keywords": ["before", "after", "clock", "edge", "stable", "metastability"],
            "answer": "Setup is the time data must be stable BEFORE the clock edge. Hold is the time data must remain stable AFTER the clock edge. Violating either causes the flip-flop to enter a metastable state."
        },
        {
            "id": "DIG_02", "type": "theory", "title": "IR Drop Impact on Timing",
            "question": "How does localized IR drop specifically lead to setup time violations on a critical timing path?",
            "keywords": ["vdd", "delay", "slows", "propagation", "drive", "threshold"],
            "answer": "Cell delay is inversely proportional to supply voltage. Localized IR drop lowers VDD, reducing gate drive strength and slowing down logic transitions. If delay increases too much, data arrives too late, causing a setup violation."
        },
        {
            "id": "DIG_03", "type": "theory", "title": "Max Frequency Formula",
            "question": "Given clock-to-Q delay (tcq), max combinational delay (tcomb), and setup time (tsu), write the inequality to find the maximum safe clock period (T).",
            "keywords": ["t", "tcq", "tcomb", "tsu", "greater", "sum"],
            "answer": "The clock period T must be greater than or equal to the sum of the delays: T >= tcq + tcomb + tsu. (Max frequency = 1/T)."
        },
        {
            "id": "DIG_04", "type": "theory", "title": "Crosstalk & SI",
            "question": "Explain crosstalk noise. How do capacitive coupling and simultaneous switching of 'aggressor' nets affect a 'victim' net?",
            "keywords": ["capacitance", "coupling", "aggressor", "victim", "glitch", "delay", "miller"],
            "answer": "Crosstalk occurs via mutual coupling capacitance between adjacent wires. When an 'aggressor' net switches rapidly, it injects charge into a nearby 'victim' net. This can cause a false voltage glitch on a static victim, or speed up/slow down a transitioning victim (Miller effect)."
        },
        {
            "id": "DIG_05", "type": "theory", "title": "Clock Skew vs Jitter",
            "question": "What is the physical difference between clock skew and clock jitter?",
            "keywords": ["skew", "spatial", "routing", "distance", "jitter", "temporal", "variation", "pll"],
            "answer": "Skew is a spatial variation: the constant difference in arrival time of the clock edge at two different physical registers due to routing imbalances. Jitter is a temporal variation: the dynamic, cycle-to-cycle uncertainty in the clock period caused by PLL noise or power supply fluctuations."
        },
        {
            "id": "DIG_06", "type": "theory", "title": "Flip-Flops vs Latches",
            "question": "What is the fundamental operational difference between an edge-triggered flip-flop and a level-sensitive latch?",
            "keywords": ["edge", "transition", "level", "transparent", "high", "low"],
            "answer": "A latch is level-sensitive (transparent); it passes data directly to the output as long as the clock is high (or low). A flip-flop is edge-triggered; it only captures and passes data exactly at the moment the clock transitions (rising or falling edge)."
        },
        {
            "id": "DIG_07", "type": "theory", "title": "Shielding Clock Nets",
            "question": "Why are critical clock nets in physical design often shielded with parallel ground (VSS) traces?",
            "keywords": ["crosstalk", "capacitance", "ground", "noise", "aggressors", "isolation"],
            "answer": "Clock nets run across the entire chip and are highly sensitive to jitter. Shielding them with VSS lines forces the coupling capacitance to terminate to a stable ground rather than a noisy adjacent signal ('aggressor'), isolating the clock from crosstalk."
        },
        {
            "id": "DIG_08", "type": "theory", "title": "Buffer Insertion",
            "question": "How does inserting buffers (repeaters) along a very long wire reduce the overall RC delay compared to a single long, unbuffered wire?",
            "keywords": ["quadratic", "linear", "break", "segments", "elmore"],
            "answer": "Unbuffered wire delay scales quadratically (L^2) with length. Inserting buffers breaks the long wire into smaller segments. The total delay becomes the sum of the linear delays of each segment plus the buffer delays, changing the delay scaling from quadratic to linear (O(L))."
        },
        {
            "id": "DIG_09", "type": "theory", "title": "Metastability & Synchronizers",
            "question": "What causes metastability in digital circuits, and how do multi-stage synchronizers resolve it across different clock domains?",
            "keywords": ["setup", "hold", "asynchronous", "probability", "settle", "two", "stages"],
            "answer": "Metastability happens when an asynchronous input violates setup/hold times. A multi-stage synchronizer (two or more flip-flops in series) gives the metastable signal an entire clock period to probabilistically settle to a valid logic level before being evaluated by the core logic."
        },
        {
            "id": "DIG_10", "type": "theory", "title": "Clock Gating",
            "question": "Explain clock gating and how it actively reduces dynamic power consumption.",
            "keywords": ["toggle", "shut", "off", "idle", "dynamic", "alpha", "activity"],
            "answer": "Clock gating uses logic gates (like an AND gate + Latch) to turn off the clock signal to idle blocks of the chip. By preventing the clock from toggling the local flip-flops and clock tree buffers, it drops the activity factor (alpha) to zero, massively saving dynamic power."
        },
        {
            "id": "DIG_11", "type": "theory", "title": "Sync vs Async Reset",
            "question": "What is the difference between an asynchronous reset and a synchronous reset in RTL design?",
            "keywords": ["clock", "edge", "immediate", "independent", "wait"],
            "answer": "An asynchronous reset clears the flip-flop immediately, independent of the clock. A synchronous reset only clears the flip-flop at the next active clock edge."
        },
        {
            "id": "DIG_12", "type": "theory", "title": "ECO Routing",
            "question": "What is an Engineering Change Order (ECO)? Why is it critical to fix SI/IR issues during the ECO phase with minimal disruption?",
            "keywords": ["signoff", "late", "stage", "timing", "placement", "ripple"],
            "answer": "ECO is a late-stage manual or semi-automated fix made to the layout after full placement and routing is complete. Minimal disruption is required because moving cells drastically will trigger a ripple effect, invalidating the existing timing closure and DRC cleanups."
        },
        {
            "id": "DIG_13", "type": "theory", "title": "On-Chip Variation (OCV)",
            "question": "In timing analysis, what is On-Chip Variation (OCV)?",
            "keywords": ["manufacturing", "doping", "temperature", "local", "pvt", "margin", "derate"],
            "answer": "OCV accounts for local microscopic manufacturing variations (doping, etching) and local temperature/voltage drops across the same die. Signoff tools apply OCV derating factors (making data paths slower and clock paths faster) to ensure the chip works despite these local variations."
        },
        {
            "id": "DIG_14", "type": "theory", "title": "Wire Spacing",
            "question": "How does increasing wire spacing impact both coupling capacitance and routing density?",
            "keywords": ["decreases", "capacitance", "crosstalk", "area", "reduces", "density"],
            "answer": "Increasing spacing exponentially decreases coupling capacitance (improving crosstalk and signal integrity). However, it consumes more track space, reducing overall routing density and potentially requiring more metal layers to complete the chip routing."
        },
        {
            "id": "DIG_15", "type": "theory", "title": "Multi-Corner Analysis (PVT)",
            "question": "Why must SI and IR drop be checked across multiple PVT (Process, Voltage, Temperature) corners?",
            "keywords": ["worst", "case", "slow", "fast", "leakage", "temperature", "voltage"],
            "answer": "Chip behavior changes wildly based on conditions. The worst-case setup time might occur at Slow-Process/Low-Voltage/High-Temp, while worst-case hold time or dynamic power might occur at Fast-Process/High-Voltage/Low-Temp. Multi-corner ensures functionality under all extreme operating extremes."
        }
    ],
    "Module 4: CAD Scripting & Algorithms": [
        {
            "id": "CODE_01", "type": "coding", "title": "Parse IR Drop Violations (Regex)",
            "question": "Write `parse_ir_violations(log_text, threshold)` to extract net names exceeding the IR drop threshold (in mV).",
            "starter": 'import re\n\ndef parse_ir_violations(log_text: str, threshold: float):\n    # Return a list of strings\n    pass\n',
            "tests": [
                {
                    "input": ("WARNING: Net VDD_CORE has IR drop = 55.4mV\nINFO: Net VDD_MEM has IR drop = 12.1mV\nNet VDD_ANA has IR drop = 82.0mV", 50.0),
                    "expected": ["VDD_CORE", "VDD_ANA"]
                }
            ]
        },
        {
            "id": "CODE_02", "type": "coding", "title": "Detect Combinational Loops (DFS)",
            "question": "Given a directed graph of logic gates represented as an adjacency list `graph`, write `has_combinational_loop(graph)` that returns True if a cycle exists.",
            "starter": 'def has_combinational_loop(graph):\n    # graph is a dict: {"gate_A": ["gate_B"], "gate_B": []}\n    pass\n',
            "tests": [
                {
                    "input": ({'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []},),
                    "expected": False
                },
                {
                    "input": ({'INV1': ['NAND1'], 'NAND1': ['NOR1'], 'NOR1': ['INV1']},),
                    "expected": True
                }
            ]
        },
        {
            "id": "CODE_03", "type": "coding", "title": "Merge Power Straps",
            "question": "Given a list of physical power strap intervals `intervals` where intervals[i] = [start, end], merge all overlapping intervals.",
            "starter": 'def merge_straps(intervals):\n    # Return merged list of intervals\n    pass\n',
            "tests": [
                {
                    "input": ([[1, 3], [2, 6], [8, 10]],),
                    "expected": [[1, 6], [8, 10]]
                },
                {
                    "input": ([[1, 4], [4, 5]],),
                    "expected": [[1, 5]]
                }
            ]
        },
        {
            "id": "CODE_04", "type": "coding", "title": "Valid Anagram (Cell Names)",
            "question": "Write a function `is_anagram(s: str, t: str) -> bool` to determine if two parameterized cell strings contain the exact same characters. (O(N) time complexity).",
            "starter": 'def is_anagram(s: str, t: str) -> bool:\n    # Write your O(N) hashing solution here\n    pass\n',
            "tests": [
                {
                    "input": ("AND2X4", "X4AND2"),
                    "expected": True
                },
                {
                    "input": ("NAND", "NOR2"),
                    "expected": False
                }
            ]
        },
        {
            "id": "CODE_05", "type": "coding", "title": "Two Sum (Resistance Matching)",
            "question": "Given an array of metal trace resistances `resistors` and a `target` resistance, return the indices of the two resistors that add up to `target`.",
            "starter": 'def two_sum(resistors, target):\n    # Return list of two indices\n    pass\n',
            "tests": [
                {
                    "input": ([2, 7, 11, 15], 9),
                    "expected": [0, 1]
                },
                {
                    "input": ([3, 2, 4], 6),
                    "expected": [1, 2]
                }
            ]
        },
        {
            "id": "CODE_06", "type": "coding", "title": "Top K Frequent EM Violations",
            "question": "Given a list of EM violation strings `errors` and an integer `k`, return the `k` most frequent violation types. Return them in any order.",
            "starter": 'def top_k_errors(errors, k):\n    # Use a dictionary/hash map\n    pass\n',
            "tests": [
                {
                    "input": (["WIDTH_ERR", "SPACE_ERR", "WIDTH_ERR", "VIA_ERR", "WIDTH_ERR", "SPACE_ERR"], 2),
                    "expected": ["WIDTH_ERR", "SPACE_ERR"]
                }
            ]
        },
        {
            "id": "CODE_07", "type": "coding", "title": "Longest Unique Substring (Metal Layers)",
            "question": "Given a string `s` representing a sequence of metal layer transitions (e.g. 'abcabcbb'), find the length of the longest contiguous substring without repeating characters.",
            "starter": 'def length_of_longest_substring(s: str) -> int:\n    # Use a sliding window algorithm\n    pass\n',
            "tests": [
                {
                    "input": ("abcabcbb",),
                    "expected": 3
                },
                {
                    "input": ("bbbbb",),
                    "expected": 1
                }
            ]
        },
        {
            "id": "CODE_08", "type": "coding", "title": "Valid Parentheses (Netlist Parsing)",
            "question": "When parsing a SPICE netlist, you must ensure parentheses/brackets are closed properly. Write a stack-based algorithm `is_valid(s: str) -> bool` to check if a string like '{[()]}' is valid.",
            "starter": 'def is_valid(s: str) -> bool:\n    # Use a stack data structure\n    pass\n',
            "tests": [
                {
                    "input": ("{[()]}",),
                    "expected": True
                },
                {
                    "input": ("{[(])}",),
                    "expected": False
                }
            ]
        },
        {
            "id": "CODE_09", "type": "coding", "title": "Max Depth of Hierarchy (Tree)",
            "question": "A chip design is a hierarchical Tree. You are given a nested list where each list represents a child block. E.g., [1, [2, [3]]] has a depth of 3. Write a recursive function `max_depth(hierarchy)`.",
            "starter": 'def max_depth(hierarchy) -> int:\n    # hierarchy is a nested list\n    pass\n',
            "tests": [
                {
                    "input": ([1, [2, [3, 4], 5], 6],),
                    "expected": 3
                },
                {
                    "input": ([1, 2, 3],),
                    "expected": 1
                }
            ]
        },
        {
            "id": "CODE_10", "type": "coding", "title": "Number of Islands (Power Grid Check)",
            "question": "Given a 2D grid where '1' represents a connected power pad and '0' is empty space, write `num_islands(grid)` to count the number of isolated power grid 'islands'.",
            "starter": 'def num_islands(grid) -> int:\n    # Use BFS or DFS to traverse the matrix\n    pass\n',
            "tests": [
                {
                    "input": ([["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]],),
                    "expected": 3
                }
            ]
        }
    ]
}

# ==============================================================================
# PYQT6 APPLICATION GUI
# ==============================================================================
class EMIRPrepApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMD EM/IR CAD Simulator - Dark Mode")
        self.resize(1200, 800)
        self.setup_dark_theme()
        
        self.current_module = list(DATA.keys())[0]
        self.current_q_idx = 0
        
        self.init_ui()
        self.load_tree()
        self.display_question(self.current_module, self.current_q_idx)

    def setup_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #E0E0E0; font-family: 'Segoe UI', sans-serif; }
            QTreeWidget { background-color: #1E1E1E; color: #E0E0E0; border: none; font-size: 14px; }
            QTreeWidget::item:selected { background-color: #2D2D2D; color: #00FF88; }
            QTextBrowser { background-color: #1E1E1E; color: #CCCCCC; border: 1px solid #333; padding: 10px; font-size: 14px; }
            QTextEdit { background-color: #1E1E1E; color: #FFFFFF; border: 1px solid #00FF88; padding: 10px; font-size: 14px; font-family: 'Consolas', monospace; }
            QPushButton { background-color: #00FF88; color: #121212; font-weight: bold; border-radius: 4px; padding: 8px 16px; font-size: 14px; }
            QPushButton:hover { background-color: #00CC6A; }
            QPushButton#sol_btn { background-color: #444; color: #FFF; }
            QPushButton#sol_btn:hover { background-color: #555; }
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Splitter for Sidebar and Main Content
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Sidebar
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_tree_click)
        self.splitter.addWidget(self.tree)

        # Main Workspace (Stacked to flip between Theory/Coding)
        self.stack = QStackedWidget()
        self.splitter.addWidget(self.stack)
        self.splitter.setSizes([300, 900])

        # Setup Theory Page
        self.theory_page = QWidget()
        theory_layout = QVBoxLayout(self.theory_page)
        
        self.th_title = QLabel("Title")
        self.th_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00FF88;")
        theory_layout.addWidget(self.th_title)
        
        self.th_prompt = QTextBrowser()
        self.th_prompt.setMaximumHeight(80)
        theory_layout.addWidget(self.th_prompt)
        
        theory_layout.addWidget(QLabel("Your Answer (Auto-Grader looks for technical keywords):"))
        self.th_editor = QTextEdit()
        theory_layout.addWidget(self.th_editor)
        
        btn_layout = QHBoxLayout()
        self.btn_submit = QPushButton("Submit & Auto-Grade")
        self.btn_submit.clicked.connect(self.grade_theory)
        self.btn_toggle_sol = QPushButton("Show Model Answer")
        self.btn_toggle_sol.setObjectName("sol_btn")
        self.btn_toggle_sol.clicked.connect(self.toggle_solution)
        btn_layout.addWidget(self.btn_submit)
        btn_layout.addWidget(self.btn_toggle_sol)
        theory_layout.addLayout(btn_layout)

        self.th_feedback = QTextBrowser()
        self.th_feedback.setMaximumHeight(150)
        self.th_feedback.hide()
        theory_layout.addWidget(self.th_feedback)
        
        self.stack.addWidget(self.theory_page)

        # Setup Coding Page
        self.code_page = QWidget()
        code_layout = QVBoxLayout(self.code_page)
        
        self.cd_title = QLabel("Title")
        self.cd_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00FF88;")
        code_layout.addWidget(self.cd_title)
        
        self.cd_prompt = QTextBrowser()
        self.cd_prompt.setMaximumHeight(80)
        code_layout.addWidget(self.cd_prompt)
        
        self.cd_editor = QTextEdit()
        code_layout.addWidget(self.cd_editor)
        
        self.btn_run = QPushButton("Run Test Cases")
        self.btn_run.clicked.connect(self.run_code)
        code_layout.addWidget(self.btn_run)
        
        self.cd_console = QTextBrowser()
        self.cd_console.setStyleSheet("color: #00FF00; background-color: #000; font-family: 'Consolas';")
        code_layout.addWidget(self.cd_console)
        
        self.stack.addWidget(self.code_page)

    def load_tree(self):
        for mod_name, questions in DATA.items():
            mod_item = QTreeWidgetItem(self.tree, [mod_name])
            mod_item.setExpanded(True)
            for idx, q in enumerate(questions):
                q_item = QTreeWidgetItem(mod_item, [f"• {q['title']}"])
                q_item.setData(0, Qt.ItemDataRole.UserRole, (mod_name, idx))

    def on_tree_click(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.display_question(data[0], data[1])

    def display_question(self, mod_name, idx):
        self.current_module = mod_name
        self.current_q_idx = idx
        q_data = DATA[mod_name][idx]

        if q_data["type"] == "theory":
            self.stack.setCurrentWidget(self.theory_page)
            self.th_title.setText(f"[{q_data['id']}] {q_data['title']}")
            self.th_prompt.setText(q_data["question"])
            self.th_editor.clear()
            self.th_feedback.hide()
        else:
            self.stack.setCurrentWidget(self.code_page)
            self.cd_title.setText(f"[{q_data['id']}] {q_data['title']}")
            self.cd_prompt.setText(q_data["question"])
            self.cd_editor.setPlainText(q_data["starter"])
            self.cd_console.clear()

    def grade_theory(self):
        q_data = DATA[self.current_module][self.current_q_idx]
        user_ans = self.th_editor.toPlainText().lower()
        keywords = q_data["keywords"]
        
        matched = []
        missed = []
        for kw in keywords:
            if kw.lower() in user_ans:
                matched.append(kw)
            else:
                missed.append(kw)
                
        score = int((len(matched) / len(keywords)) * 100)
        
        color = "#00FF88" if score >= 70 else "#FF4444"
        feedback = f"<h2 style='color:{color}; margin:0;'>Score: {score}%</h2>"
        feedback += f"<p><b>Matched Keywords:</b> {', '.join(matched) if matched else 'None'}</p>"
        if missed:
            feedback += f"<p><b>Missed Keywords:</b> <span style='color:#FF4444;'>{', '.join(missed)}</span></p>"
        
        self.th_feedback.setHtml(feedback)
        self.th_feedback.show()

    def toggle_solution(self):
        q_data = DATA[self.current_module][self.current_q_idx]
        if self.th_feedback.isVisible() and "MODEL ANSWER" in self.th_feedback.toPlainText():
            self.th_feedback.hide()
        else:
            self.th_feedback.setHtml(f"<h3 style='color:#00FF88;'>MODEL ANSWER:</h3><p>{q_data['answer']}</p>")
            self.th_feedback.show()

    def run_code(self):
        q_data = DATA[self.current_module][self.current_q_idx]
        code = self.cd_editor.toPlainText()
        self.cd_console.clear()
        
        buffer = io.StringIO()
        sys.stdout = buffer
        exec_globals = {}
        
        try:
            exec(code, exec_globals)
        except Exception as e:
            sys.stdout = sys.__stdout__
            self.cd_console.setText(f"[SYNTAX/RUNTIME ERROR]\n{traceback.format_exc()}")
            return
        finally:
            sys.stdout = sys.__stdout__

        stdout_val = buffer.getvalue()
        output_text = f"[STDOUT]\n{stdout_val}\n" if stdout_val else ""
        
        func_name = q_data["starter"].split("(")[0].replace("def ", "").strip()
        if func_name not in exec_globals:
            self.cd_console.setText(f"❌ Error: Could not find function '{func_name}'")
            return
            
        user_func = exec_globals[func_name]
        tests = q_data["tests"]
        passed = 0
        
        for i, test in enumerate(tests, 1):
            inputs = test["input"]
            expected = test["expected"]
            try:
                res = user_func(*inputs) if isinstance(inputs, tuple) else user_func(inputs)
                if res == expected:
                    output_text += f"✅ Test {i}: PASSED\n"
                    passed += 1
                else:
                    output_text += f"❌ Test {i}: FAILED\n   Expected: {expected}\n   Got: {res}\n"
            except Exception as err:
                output_text += f"💥 Test {i}: ERROR\n{err}\n"
                
        output_text += f"\nRESULTS: {passed}/{len(tests)} Passed"
        self.cd_console.setText(output_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EMIRPrepApp()
    window.show()
    sys.exit(app.exec())