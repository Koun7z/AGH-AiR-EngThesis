clear;

syms omega_x omega_y omega_z real
syms Delta_t real
syms q_r q_i q_j q_k real
syms sigma_w_x sigma_w_y sigma_w_z real

sympref('AbbreviateOutput', true);

syms g_i g_j g_k a_i a_j a_k real


assume(g_i^2 + g_j^2 + g_k^2 == 1)
assume(a_i^2 + a_j^2 + a_k^2 == 1)
assume(q_r^2 + q_i^2 + q_j^2 + q_k^2 == 1)

q = [q_r; q_i; q_j; q_k];
a = [a_i; a_j; a_k];
g = [0; 0; 1];
%%
% find q that rotates g into a R(q)*g = a => R(q)*g - a = 0
eqs = squatrotate(q, g) - a %[output:32c347b2]
eqs = simplify(subs(eqs, q_k, 0)) % assume q_k = 0 %[output:9c96c71c]
eqs = [eqs; q_r^2 + q_i ^ 2 + q_j ^ 2 - 1];
assume(q_r > 0)

solve(eqs, [q_r q_i q_j], "Real", true, "ReturnConditions",true) %[output:0144447e]
%%
g = [g_i; g_j; g_k];

ddot = g.'*a;
ccross = cross(g, a);

Q = [1 + ddot; ccross] %[output:1c0b2e37]


%[appendix]{"version":"1.0"}
%---
%[metadata:view]
%   data: {"layout":"inline"}
%---
%[output:32c347b2]
%   data: {"dataType":"symbolic","outputData":{"name":"eqs","value":"\\left(\\begin{array}{c}\n2\\,q_i \\,q_k -a_i +2\\,q_j \\,q_r \\\\\n2\\,q_j \\,q_k -a_j -2\\,q_i \\,q_r \\\\\n-2\\,{q_i }^2 -2\\,{q_j }^2 -a_k +1\n\\end{array}\\right)"}}
%---
%[output:9c96c71c]
%   data: {"dataType":"symbolic","outputData":{"name":"eqs","value":"\\left(\\begin{array}{c}\n2\\,q_j \\,q_r -a_i \\\\\n-a_j -2\\,q_i \\,q_r \\\\\n-2\\,{q_i }^2 -2\\,{q_j }^2 -a_k +1\n\\end{array}\\right)"}}
%---
%[output:0144447e]
%   data: {"dataType":"textualVariable","outputData":{"header":"struct with fields:","name":"ans","value":"           q_r: 1\n           q_i: 0\n           q_j: 0\n    parameters: [1×0 sym]\n    conditions: a_i == 0 & a_j == 0 & a_k == 1\n"}}
%---
%[output:1c0b2e37]
%   data: {"dataType":"symbolic","outputData":{"name":"Q","value":"\\left(\\begin{array}{c}\na_i \\,g_i +a_j \\,g_j +a_k \\,g_k +1\\\\\na_k \\,g_j -a_j \\,g_k \\\\\na_i \\,g_k -a_k \\,g_i \\\\\na_j \\,g_i -a_i \\,g_j \n\\end{array}\\right)"}}
%---
