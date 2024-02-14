% List all files recursively in a directory
directory = 'hdrvdp-3.0.7';

% Get a list of all files and directories in the current directory
contents = dir(fullfile(directory, '**', '*'));

% Filter out directories
file_mask = ~[contents.isdir];
files = contents(file_mask);

% Initialize cell array to store full paths
fn_list = cell(numel(files), 1);
data_list = cell(numel(files), 1);

% Concatenate folder and name properties to get full paths
for i = 1:numel(files)
    if endsWith(files(i).name, 'Contents.m')
        continue;
    end
    if endsWith(files(i).name, '.m')
        fn_list{i} = fullfile(files(i).folder, files(i).name);
    else
        data_list{i} = fullfile(files(i).folder, files(i).name);
    end
end

% Remove empty entries (files ending with ".m" were excluded)
fn_list = fn_list(~cellfun('isempty', fn_list));
data_list = data_list(~cellfun('isempty', data_list));

opts = compiler.build.PythonPackageOptions(fn_list, ...
    'AdditionalFiles', data_list, ...
    'OutputDir', '/MATLAB Drive/hdrpy', ...
    'PackageName', 'hdrpy');

compileResult = compiler.build.pythonPackage(opts);

