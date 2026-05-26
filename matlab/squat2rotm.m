function [ rotm ] = squat2rotm(q, opts)
%squat2rotm Converts the quaternion to a rotation matrix
%   

    arguments
        q                  %(1, 4) symbolic
        opts.AssumeUnitNorm (1, 1) logical = true
        opts.FullDiagonal   (1, 1) logical = false
    end

    [r,c] = size(q);
    if (r ~= 4 || c ~= 1 )
        error("Quaternion need to be an 4 element colum vector")
    end

    q_r = q(1);
    q_i = q(2);
    q_j = q(3);
    q_k = q(4);

    if (opts.AssumeUnitNorm)
        s = 1;
    else
        s = q_r ^ 2 + q_i ^ 2 + q_j ^ 2 + q_k ^ 2; %TODO
    end
    
    if(opts.FullDiagonal)
        rotm = [q_r ^ 2 + q_i ^ 2 - q_j ^ 2 - q_k ^ 2, 2 * (q_i * q_j - q_k * q_r), 2 * (q_i * q_k + q_j * q_r);
                2 * (q_i * q_j + q_k * q_r), q_r ^ 2 - q_i ^ 2 + q_j ^ 2 - q_k ^ 2, 2 * (q_j * q_k - q_i * q_r);
                2 * (q_i * q_k - q_j * q_r), 2 * (q_j * q_k + q_i * q_r), q_r ^ 2 - q_i ^ 2 - q_j ^ 2 + q_k ^ 2];
    else
        rotm = [1 - 2 * (q_j ^ 2 + q_k ^ 2), 2 * (q_i * q_j - q_k * q_r), 2 * (q_i * q_k + q_j * q_r);
                2 * (q_i * q_j + q_k * q_r), 1 - 2 * (q_i ^ 2 + q_k ^ 2), 2 * (q_j * q_k - q_i * q_r);
                2 * (q_i * q_k - q_j * q_r), 2 * (q_j * q_k + q_i * q_r), 1 - 2 * (q_i ^ 2 + q_j ^ 2)];
    end
    

end