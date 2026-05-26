syms omega_x omega_y omega_z
syms Delta_t
syms q_r q_i q_j q_k
syms sigma_w_x sigma_w_y sigma_w_z

sympref('AbbreviateOutput', true);

q = [q_r; q_i; q_j; q_k];
Sigma = diag([sigma_w_x ^ 2 sigma_w_y ^ 2 sigma_w_z ^ 2]);
omega = [omega_x; omega_y; omega_z] %[output:4f0d334c]

% First order attitude propagation
q_n = q + squatmul(q, [0; omega_x; omega_y; omega_z]) * Delta_t  / 2 %[output:879571bd]

F = jacobian(q_n, q) %[output:361c68fb]

W = jacobian(q_n, [omega_x omega_y omega_z]) %[output:2e020218]
Q = simplify(W * Sigma * W.');
%%
syms g_x g_y g_z
sympref('AbbreviateOutput', false);

g = [g_x; g_y; g_z];

C =  simplify(squat2rotm(q.', AssumeUnitNorm=true, FullDiagonal=true)) %[output:0cf0cce8]

% Measurement model
h_a = C.' * g %[output:1cbf85dc]

% Meatement model jacobian
H_a = jacobian(h_a, q) %[output:09c60bd5]

% We will always rotate g = [0;0;1] to the sensor frame so we can 
% simplify the measurement model a lot

sympref('AbbreviateOutput', true);

h_a = subs(h_a, g, [0; 0; 1]) %[output:94e9dea6]
H_a = jacobian(h_a, q) %[output:30aa50db]
%%
sympref('AbbreviateOutput', true);

syms sigma_ax sigma_ay sigma_az;

R = diag([sigma_ax sigma_ay sigma_az]) %[output:59c9e8b2]

H = H_a %[output:0c53334c]
H_T = H.' %[output:061bd923]


% With magnetometer
%H = [H_a; H_m] 

P = sym('P', [4 4]);

% Calculating those solutions symbolicly makes no sense anymore
% S = simplify(H * P * H.' + R);
% K = P * H.' * inv(S)

% y = z - h;
% x = \hat{x} + K * y
% P = (I - K*H)hat{P}
%%

S = sym('S', [3 3]) %[output:1b360788]

PH_T = sym("PH", [4 3]) %[output:6acb0640]

inv(S) %[output:58e441ec]
% TODO this might actualy be faster then full numeric solve...
K = PH_T / S %[output:917ab45e]

%[appendix]{"version":"1.0"}
%---
%[metadata:view]
%   data: {"layout":"inline"}
%---
%[output:4f0d334c]
%   data: {"dataType":"symbolic","outputData":{"name":"omega","value":"\\left(\\begin{array}{c}\n\\omega_x \\\\\n\\omega_y \\\\\n\\omega_z \n\\end{array}\\right)"}}
%---
%[output:879571bd]
%   data: {"dataType":"symbolic","outputData":{"name":"q_n","value":"\\left(\\begin{array}{c}\nq_r -\\frac{\\Delta_t \\,{\\left(\\omega_x \\,q_i +\\omega_y \\,q_j +\\omega_z \\,q_k \\right)}}{2}\\\\\nq_i +\\frac{\\Delta_t \\,{\\left(\\omega_z \\,q_j -\\omega_y \\,q_k +\\omega_x \\,q_r \\right)}}{2}\\\\\nq_j +\\frac{\\Delta_t \\,{\\left(\\omega_x \\,q_k -\\omega_z \\,q_i +\\omega_y \\,q_r \\right)}}{2}\\\\\nq_k +\\frac{\\Delta_t \\,{\\left(\\omega_y \\,q_i -\\omega_x \\,q_j +\\omega_z \\,q_r \\right)}}{2}\n\\end{array}\\right)"}}
%---
%[output:361c68fb]
%   data: {"dataType":"symbolic","outputData":{"name":"F","value":"\\left(\\begin{array}{cccc}\n1 & -\\frac{\\Delta_t \\,\\omega_x }{2} & -\\frac{\\Delta_t \\,\\omega_y }{2} & -\\frac{\\Delta_t \\,\\omega_z }{2}\\\\\n\\frac{\\Delta_t \\,\\omega_x }{2} & 1 & \\frac{\\Delta_t \\,\\omega_z }{2} & -\\frac{\\Delta_t \\,\\omega_y }{2}\\\\\n\\frac{\\Delta_t \\,\\omega_y }{2} & -\\frac{\\Delta_t \\,\\omega_z }{2} & 1 & \\frac{\\Delta_t \\,\\omega_x }{2}\\\\\n\\frac{\\Delta_t \\,\\omega_z }{2} & \\frac{\\Delta_t \\,\\omega_y }{2} & -\\frac{\\Delta_t \\,\\omega_x }{2} & 1\n\\end{array}\\right)"}}
%---
%[output:2e020218]
%   data: {"dataType":"symbolic","outputData":{"name":"W","value":"\\left(\\begin{array}{ccc}\n-\\frac{\\Delta_t \\,q_i }{2} & -\\frac{\\Delta_t \\,q_j }{2} & -\\frac{\\Delta_t \\,q_k }{2}\\\\\n\\frac{\\Delta_t \\,q_r }{2} & -\\frac{\\Delta_t \\,q_k }{2} & \\frac{\\Delta_t \\,q_j }{2}\\\\\n\\frac{\\Delta_t \\,q_k }{2} & \\frac{\\Delta_t \\,q_r }{2} & -\\frac{\\Delta_t \\,q_i }{2}\\\\\n-\\frac{\\Delta_t \\,q_j }{2} & \\frac{\\Delta_t \\,q_i }{2} & \\frac{\\Delta_t \\,q_r }{2}\n\\end{array}\\right)"}}
%---
%[output:0cf0cce8]
%   data: {"dataType":"symbolic","outputData":{"name":"C","value":"\\left(\\begin{array}{ccc}\n{q_i }^2 -{q_j }^2 -{q_k }^2 +{q_r }^2  & 2\\,q_i \\,q_j -2\\,q_k \\,q_r  & 2\\,q_i \\,q_k +2\\,q_j \\,q_r \\\\\n2\\,q_i \\,q_j +2\\,q_k \\,q_r  & -{q_i }^2 +{q_j }^2 -{q_k }^2 +{q_r }^2  & 2\\,q_j \\,q_k -2\\,q_i \\,q_r \\\\\n2\\,q_i \\,q_k -2\\,q_j \\,q_r  & 2\\,q_j \\,q_k +2\\,q_i \\,q_r  & -{q_i }^2 -{q_j }^2 +{q_k }^2 +{q_r }^2 \n\\end{array}\\right)"}}
%---
%[output:1cbf85dc]
%   data: {"dataType":"symbolic","outputData":{"name":"h_a","value":"\\left(\\begin{array}{c}\ng_x \\,{\\left({q_i }^2 -{q_j }^2 -{q_k }^2 +{q_r }^2 \\right)}+g_y \\,{\\left(2\\,q_i \\,q_j +2\\,q_k \\,q_r \\right)}+g_z \\,{\\left(2\\,q_i \\,q_k -2\\,q_j \\,q_r \\right)}\\\\\ng_x \\,{\\left(2\\,q_i \\,q_j -2\\,q_k \\,q_r \\right)}-g_y \\,{\\left({q_i }^2 -{q_j }^2 +{q_k }^2 -{q_r }^2 \\right)}+g_z \\,{\\left(2\\,q_j \\,q_k +2\\,q_i \\,q_r \\right)}\\\\\ng_x \\,{\\left(2\\,q_i \\,q_k +2\\,q_j \\,q_r \\right)}-g_z \\,{\\left({q_i }^2 +{q_j }^2 -{q_k }^2 -{q_r }^2 \\right)}+g_y \\,{\\left(2\\,q_j \\,q_k -2\\,q_i \\,q_r \\right)}\n\\end{array}\\right)"}}
%---
%[output:09c60bd5]
%   data: {"dataType":"symbolic","outputData":{"name":"H_a","value":"\\left(\\begin{array}{cccc}\n2\\,g_y \\,q_k -2\\,g_z \\,q_j +2\\,g_x \\,q_r  & 2\\,g_x \\,q_i +2\\,g_y \\,q_j +2\\,g_z \\,q_k  & 2\\,g_y \\,q_i -2\\,g_x \\,q_j -2\\,g_z \\,q_r  & 2\\,g_z \\,q_i -2\\,g_x \\,q_k +2\\,g_y \\,q_r \\\\\n2\\,g_z \\,q_i -2\\,g_x \\,q_k +2\\,g_y \\,q_r  & 2\\,g_x \\,q_j -2\\,g_y \\,q_i +2\\,g_z \\,q_r  & 2\\,g_x \\,q_i +2\\,g_y \\,q_j +2\\,g_z \\,q_k  & 2\\,g_z \\,q_j -2\\,g_y \\,q_k -2\\,g_x \\,q_r \\\\\n2\\,g_x \\,q_j -2\\,g_y \\,q_i +2\\,g_z \\,q_r  & 2\\,g_x \\,q_k -2\\,g_z \\,q_i -2\\,g_y \\,q_r  & 2\\,g_y \\,q_k -2\\,g_z \\,q_j +2\\,g_x \\,q_r  & 2\\,g_x \\,q_i +2\\,g_y \\,q_j +2\\,g_z \\,q_k \n\\end{array}\\right)"}}
%---
%[output:94e9dea6]
%   data: {"dataType":"symbolic","outputData":{"name":"h_a","value":"\\left(\\begin{array}{c}\n2\\,q_i \\,q_k -2\\,q_j \\,q_r \\\\\n2\\,q_j \\,q_k +2\\,q_i \\,q_r \\\\\n-{q_i }^2 -{q_j }^2 +{q_k }^2 +{q_r }^2 \n\\end{array}\\right)"}}
%---
%[output:30aa50db]
%   data: {"dataType":"symbolic","outputData":{"name":"H_a","value":"\\left(\\begin{array}{cccc}\n-2\\,q_j  & 2\\,q_k  & -2\\,q_r  & 2\\,q_i \\\\\n2\\,q_i  & 2\\,q_r  & 2\\,q_k  & 2\\,q_j \\\\\n2\\,q_r  & -2\\,q_i  & -2\\,q_j  & 2\\,q_k \n\\end{array}\\right)"}}
%---
%[output:59c9e8b2]
%   data: {"dataType":"symbolic","outputData":{"name":"R","value":"\\left(\\begin{array}{ccc}\n\\sigma_{\\textrm{ax}}  & 0 & 0\\\\\n0 & \\sigma_{\\textrm{ay}}  & 0\\\\\n0 & 0 & \\sigma_{\\textrm{az}} \n\\end{array}\\right)"}}
%---
%[output:0c53334c]
%   data: {"dataType":"symbolic","outputData":{"name":"H","value":"\\left(\\begin{array}{cccc}\n-2\\,q_j  & 2\\,q_k  & -2\\,q_r  & 2\\,q_i \\\\\n2\\,q_i  & 2\\,q_r  & 2\\,q_k  & 2\\,q_j \\\\\n2\\,q_r  & -2\\,q_i  & -2\\,q_j  & 2\\,q_k \n\\end{array}\\right)"}}
%---
%[output:061bd923]
%   data: {"dataType":"symbolic","outputData":{"name":"H_T","value":"\\left(\\begin{array}{ccc}\n-2\\,q_j  & 2\\,q_i  & 2\\,q_r \\\\\n2\\,q_k  & 2\\,q_r  & -2\\,q_i \\\\\n-2\\,q_r  & 2\\,q_k  & -2\\,q_j \\\\\n2\\,q_i  & 2\\,q_j  & 2\\,q_k \n\\end{array}\\right)"}}
%---
%[output:1b360788]
%   data: {"dataType":"symbolic","outputData":{"name":"S","value":"\\left(\\begin{array}{ccc}\nS_{1,1}  & S_{1,2}  & S_{1,3} \\\\\nS_{2,1}  & S_{2,2}  & S_{2,3} \\\\\nS_{3,1}  & S_{3,2}  & S_{3,3} \n\\end{array}\\right)"}}
%---
%[output:6acb0640]
%   data: {"dataType":"symbolic","outputData":{"name":"PH_T","value":"\\left(\\begin{array}{ccc}\n{\\textrm{PH}}_{1,1}  & {\\textrm{PH}}_{1,2}  & {\\textrm{PH}}_{1,3} \\\\\n{\\textrm{PH}}_{2,1}  & {\\textrm{PH}}_{2,2}  & {\\textrm{PH}}_{2,3} \\\\\n{\\textrm{PH}}_{3,1}  & {\\textrm{PH}}_{3,2}  & {\\textrm{PH}}_{3,3} \\\\\n{\\textrm{PH}}_{4,1}  & {\\textrm{PH}}_{4,2}  & {\\textrm{PH}}_{4,3} \n\\end{array}\\right)"}}
%---
%[output:58e441ec]
%   data: {"dataType":"symbolic","outputData":{"name":"ans","value":"\\begin{array}{l}\n\\left(\\begin{array}{ccc}\n\\frac{S_{2,2} \\,S_{3,3} -S_{2,3} \\,S_{3,2} }{\\sigma_1 } & -\\frac{S_{1,2} \\,S_{3,3} -S_{1,3} \\,S_{3,2} }{\\sigma_1 } & \\frac{S_{1,2} \\,S_{2,3} -S_{1,3} \\,S_{2,2} }{\\sigma_1 }\\\\\n-\\frac{S_{2,1} \\,S_{3,3} -S_{2,3} \\,S_{3,1} }{\\sigma_1 } & \\frac{S_{1,1} \\,S_{3,3} -S_{1,3} \\,S_{3,1} }{\\sigma_1 } & -\\frac{S_{1,1} \\,S_{2,3} -S_{1,3} \\,S_{2,1} }{\\sigma_1 }\\\\\n\\frac{S_{2,1} \\,S_{3,2} -S_{2,2} \\,S_{3,1} }{\\sigma_1 } & -\\frac{S_{1,1} \\,S_{3,2} -S_{1,2} \\,S_{3,1} }{\\sigma_1 } & \\frac{S_{1,1} \\,S_{2,2} -S_{1,2} \\,S_{2,1} }{\\sigma_1 }\n\\end{array}\\right)\\\\\n\\mathrm{}\\\\\n\\textrm{where}\\\\\n\\mathrm{}\\\\\n\\;\\;\\sigma_1 =S_{1,1} \\,S_{2,2} \\,S_{3,3} -S_{1,1} \\,S_{2,3} \\,S_{3,2} -S_{1,2} \\,S_{2,1} \\,S_{3,3} +S_{1,2} \\,S_{2,3} \\,S_{3,1} +S_{1,3} \\,S_{2,1} \\,S_{3,2} -S_{1,3} \\,S_{2,2} \\,S_{3,1} \n\\end{array}"}}
%---
%[output:917ab45e]
%   data: {"dataType":"symbolic","outputData":{"name":"K","value":"\\begin{array}{l}\n\\left(\\begin{array}{ccc}\n\\frac{{\\textrm{PH}}_{1,1} \\,S_{2,2} \\,S_{3,3} -{\\textrm{PH}}_{1,1} \\,S_{2,3} \\,S_{3,2} -{\\textrm{PH}}_{1,2} \\,S_{2,1} \\,S_{3,3} +{\\textrm{PH}}_{1,2} \\,S_{2,3} \\,S_{3,1} +{\\textrm{PH}}_{1,3} \\,S_{2,1} \\,S_{3,2} -{\\textrm{PH}}_{1,3} \\,S_{2,2} \\,S_{3,1} }{\\sigma_1 } & -\\frac{{\\textrm{PH}}_{1,1} \\,S_{1,2} \\,S_{3,3} -{\\textrm{PH}}_{1,1} \\,S_{1,3} \\,S_{3,2} -{\\textrm{PH}}_{1,2} \\,S_{1,1} \\,S_{3,3} +{\\textrm{PH}}_{1,2} \\,S_{1,3} \\,S_{3,1} +{\\textrm{PH}}_{1,3} \\,S_{1,1} \\,S_{3,2} -{\\textrm{PH}}_{1,3} \\,S_{1,2} \\,S_{3,1} }{\\sigma_1 } & \\frac{{\\textrm{PH}}_{1,1} \\,S_{1,2} \\,S_{2,3} -{\\textrm{PH}}_{1,1} \\,S_{1,3} \\,S_{2,2} -{\\textrm{PH}}_{1,2} \\,S_{1,1} \\,S_{2,3} +{\\textrm{PH}}_{1,2} \\,S_{1,3} \\,S_{2,1} +{\\textrm{PH}}_{1,3} \\,S_{1,1} \\,S_{2,2} -{\\textrm{PH}}_{1,3} \\,S_{1,2} \\,S_{2,1} }{\\sigma_1 }\\\\\n\\frac{{\\textrm{PH}}_{2,1} \\,S_{2,2} \\,S_{3,3} -{\\textrm{PH}}_{2,1} \\,S_{2,3} \\,S_{3,2} -{\\textrm{PH}}_{2,2} \\,S_{2,1} \\,S_{3,3} +{\\textrm{PH}}_{2,2} \\,S_{2,3} \\,S_{3,1} +{\\textrm{PH}}_{2,3} \\,S_{2,1} \\,S_{3,2} -{\\textrm{PH}}_{2,3} \\,S_{2,2} \\,S_{3,1} }{\\sigma_1 } & -\\frac{{\\textrm{PH}}_{2,1} \\,S_{1,2} \\,S_{3,3} -{\\textrm{PH}}_{2,1} \\,S_{1,3} \\,S_{3,2} -{\\textrm{PH}}_{2,2} \\,S_{1,1} \\,S_{3,3} +{\\textrm{PH}}_{2,2} \\,S_{1,3} \\,S_{3,1} +{\\textrm{PH}}_{2,3} \\,S_{1,1} \\,S_{3,2} -{\\textrm{PH}}_{2,3} \\,S_{1,2} \\,S_{3,1} }{\\sigma_1 } & \\frac{{\\textrm{PH}}_{2,1} \\,S_{1,2} \\,S_{2,3} -{\\textrm{PH}}_{2,1} \\,S_{1,3} \\,S_{2,2} -{\\textrm{PH}}_{2,2} \\,S_{1,1} \\,S_{2,3} +{\\textrm{PH}}_{2,2} \\,S_{1,3} \\,S_{2,1} +{\\textrm{PH}}_{2,3} \\,S_{1,1} \\,S_{2,2} -{\\textrm{PH}}_{2,3} \\,S_{1,2} \\,S_{2,1} }{\\sigma_1 }\\\\\n\\frac{{\\textrm{PH}}_{3,1} \\,S_{2,2} \\,S_{3,3} -{\\textrm{PH}}_{3,1} \\,S_{2,3} \\,S_{3,2} -{\\textrm{PH}}_{3,2} \\,S_{2,1} \\,S_{3,3} +{\\textrm{PH}}_{3,2} \\,S_{2,3} \\,S_{3,1} +{\\textrm{PH}}_{3,3} \\,S_{2,1} \\,S_{3,2} -{\\textrm{PH}}_{3,3} \\,S_{2,2} \\,S_{3,1} }{\\sigma_1 } & -\\frac{{\\textrm{PH}}_{3,1} \\,S_{1,2} \\,S_{3,3} -{\\textrm{PH}}_{3,1} \\,S_{1,3} \\,S_{3,2} -{\\textrm{PH}}_{3,2} \\,S_{1,1} \\,S_{3,3} +{\\textrm{PH}}_{3,2} \\,S_{1,3} \\,S_{3,1} +{\\textrm{PH}}_{3,3} \\,S_{1,1} \\,S_{3,2} -{\\textrm{PH}}_{3,3} \\,S_{1,2} \\,S_{3,1} }{\\sigma_1 } & \\frac{{\\textrm{PH}}_{3,1} \\,S_{1,2} \\,S_{2,3} -{\\textrm{PH}}_{3,1} \\,S_{1,3} \\,S_{2,2} -{\\textrm{PH}}_{3,2} \\,S_{1,1} \\,S_{2,3} +{\\textrm{PH}}_{3,2} \\,S_{1,3} \\,S_{2,1} +{\\textrm{PH}}_{3,3} \\,S_{1,1} \\,S_{2,2} -{\\textrm{PH}}_{3,3} \\,S_{1,2} \\,S_{2,1} }{\\sigma_1 }\\\\\n\\frac{{\\textrm{PH}}_{4,1} \\,S_{2,2} \\,S_{3,3} -{\\textrm{PH}}_{4,1} \\,S_{2,3} \\,S_{3,2} -{\\textrm{PH}}_{4,2} \\,S_{2,1} \\,S_{3,3} +{\\textrm{PH}}_{4,2} \\,S_{2,3} \\,S_{3,1} +{\\textrm{PH}}_{4,3} \\,S_{2,1} \\,S_{3,2} -{\\textrm{PH}}_{4,3} \\,S_{2,2} \\,S_{3,1} }{\\sigma_1 } & -\\frac{{\\textrm{PH}}_{4,1} \\,S_{1,2} \\,S_{3,3} -{\\textrm{PH}}_{4,1} \\,S_{1,3} \\,S_{3,2} -{\\textrm{PH}}_{4,2} \\,S_{1,1} \\,S_{3,3} +{\\textrm{PH}}_{4,2} \\,S_{1,3} \\,S_{3,1} +{\\textrm{PH}}_{4,3} \\,S_{1,1} \\,S_{3,2} -{\\textrm{PH}}_{4,3} \\,S_{1,2} \\,S_{3,1} }{\\sigma_1 } & \\frac{{\\textrm{PH}}_{4,1} \\,S_{1,2} \\,S_{2,3} -{\\textrm{PH}}_{4,1} \\,S_{1,3} \\,S_{2,2} -{\\textrm{PH}}_{4,2} \\,S_{1,1} \\,S_{2,3} +{\\textrm{PH}}_{4,2} \\,S_{1,3} \\,S_{2,1} +{\\textrm{PH}}_{4,3} \\,S_{1,1} \\,S_{2,2} -{\\textrm{PH}}_{4,3} \\,S_{1,2} \\,S_{2,1} }{\\sigma_1 }\n\\end{array}\\right)\\\\\n\\mathrm{}\\\\\n\\textrm{where}\\\\\n\\mathrm{}\\\\\n\\;\\;\\sigma_1 =S_{1,1} \\,S_{2,2} \\,S_{3,3} -S_{1,1} \\,S_{2,3} \\,S_{3,2} -S_{1,2} \\,S_{2,1} \\,S_{3,3} +S_{1,2} \\,S_{2,3} \\,S_{3,1} +S_{1,3} \\,S_{2,1} \\,S_{3,2} -S_{1,3} \\,S_{2,2} \\,S_{3,1} \n\\end{array}"}}
%---
