function [ n ] = squatrotate( q, v )
%squatrotate Rotate a vector r by a quaternion q
%   
    [r, c] = size(v);
    if(r ~= 3 || c ~= 1)
        error("V should be a 3 element column vector")
    end
    
     
    n = squat2rotm(q) * v;
end