% This script generates installer_input.txt for input
% to the Matlab Runtime installer -inputFile flag
% ./install -inputFile installer_input.txt

% Open the file for reading
fid = fopen('./hdrpy/requiredMCRProducts.txt', 'r');
fileContents = fscanf(fid, '%f');
fclose(fid);

% Destination folder
destinationFolder = '/usr/local/MATLAB/MATLAB_Runtime';

% Agree to license
agreeToLicense = 'yes';

% Log file
outputFile = 'mylog.txt';

% Need this to query product strings
pcmn = matlab.depfun.internal.ProductComponentModuleNavigator;

% Open the file for writing
fid = fopen('installer_input.txt', 'w');
fprintf(fid, 'agreeToLicense=%s\n', agreeToLicense);
fprintf(fid, 'outputFile=%s\n', outputFile);
fprintf(fid, 'destinationFolder=%s\n', destinationFolder);

% Loop through each number
for i = 1:numel(fileContents)
    number = fileContents(i);
    pInfo = pcmn.productInfo(number);
    name = pInfo.extPName;
    fprintf(fid, 'product.%s\n', name);
end


% Close the file
fclose(fid);

disp('File has been written successfully.');

