const fs = require('fs');
const { execSync } = require('child_process');

// Read the package.json file
const packageJsonPath = './package.json';
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

// Check if axios is in dependencies
if (!packageJson.dependencies.axios) {
  packageJson.dependencies.axios = "^1.6.2"; // Add axios with a recent version
  console.log('Added axios dependency to package.json');
}

// Write the updated package.json
fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));

// Run npm install to install the dependencies
console.log('Installing dependencies...');
try {
  execSync('npm install', { stdio: 'inherit' });
  console.log('Dependencies installed successfully!');
} catch (error) {
  console.error('Error installing dependencies:', error);
}
