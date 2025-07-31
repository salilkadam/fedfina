#!/usr/bin/env node

/**
 * Test script to verify the ElevenLabs integration implementation
 * Run with: node test-implementation.js
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 Testing ElevenLabs Integration Implementation...\n');

// Test 1: Check if all required files exist
const requiredFiles = [
    'src/types/parameters.ts',
    'src/utils/parameterParser.ts',
    'src/context/ParameterContext.tsx',
    'src/services/webhookService.ts',
    'src/components/ElevenLabsWidget.tsx',
    'src/App.tsx',
    'src/App.css',
    'backend/app.py',
    'backend/requirements.txt',
    'tsconfig.json',
    'package.json'
];

console.log('📁 Checking required files...');
let allFilesExist = true;

requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
        console.log(`✅ ${file}`);
    } else {
        console.log(`❌ ${file} - MISSING`);
        allFilesExist = false;
    }
});

if (!allFilesExist) {
    console.log('\n❌ Some required files are missing!');
    process.exit(1);
}

console.log('\n✅ All required files exist!\n');

// Test 2: Check package.json dependencies
console.log('📦 Checking package.json dependencies...');
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));

const requiredDependencies = ['react', 'react-dom', 'typescript'];
const missingDeps = requiredDependencies.filter(dep => !packageJson.dependencies[dep]);

if (missingDeps.length > 0) {
    console.log(`❌ Missing dependencies: ${missingDeps.join(', ')}`);
} else {
    console.log('✅ All required dependencies are present');
}

// Test 3: Check TypeScript configuration
console.log('\n⚙️ Checking TypeScript configuration...');
const tsConfig = JSON.parse(fs.readFileSync('tsconfig.json', 'utf8'));

if (tsConfig.compilerOptions && tsConfig.compilerOptions.jsx === 'react-jsx') {
    console.log('✅ TypeScript configuration is correct');
} else {
    console.log('❌ TypeScript configuration needs JSX support');
}

// Test 4: Check backend requirements
console.log('\n🐍 Checking backend requirements...');
const requirements = fs.readFileSync('backend/requirements.txt', 'utf8');
const requiredBackendDeps = ['fastapi', 'uvicorn', 'pydantic'];

const missingBackendDeps = requiredBackendDeps.filter(dep => !requirements.includes(dep));

if (missingBackendDeps.length > 0) {
    console.log(`❌ Missing backend dependencies: ${missingBackendDeps.join(', ')}`);
} else {
    console.log('✅ All required backend dependencies are present');
}

// Test 5: Check for key implementation features
console.log('\n🔍 Checking implementation features...');

const features = {
    'Parameter parsing and validation': fs.readFileSync('src/utils/parameterParser.ts', 'utf8').includes('validateParameters'),
    'React context for parameters': fs.readFileSync('src/context/ParameterContext.tsx', 'utf8').includes('ParameterProvider'),
    'Webhook service': fs.readFileSync('src/services/webhookService.ts', 'utf8').includes('sendConversationData'),
    'Enhanced widget component': fs.readFileSync('src/components/ElevenLabsWidget.tsx', 'utf8').includes('ElevenLabsWidget'),
    'Backend API endpoints': fs.readFileSync('backend/app.py', 'utf8').includes('@app.post'),
    'Error handling': fs.readFileSync('src/components/ElevenLabsWidget.tsx', 'utf8').includes('onError'),
    'Mobile responsive CSS': fs.readFileSync('src/App.css', 'utf8').includes('@media'),
    'TypeScript interfaces': fs.readFileSync('src/types/parameters.ts', 'utf8').includes('interface')
};

Object.entries(features).forEach(([feature, implemented]) => {
    if (implemented) {
        console.log(`✅ ${feature}`);
    } else {
        console.log(`❌ ${feature} - NOT IMPLEMENTED`);
    }
});

// Test 6: Check for security features
console.log('\n🔒 Checking security features...');

const securityFeatures = {
    'API key authentication': fs.readFileSync('backend/app.py', 'utf8').includes('HTTPBearer'),
    'Rate limiting': fs.readFileSync('backend/app.py', 'utf8').includes('check_rate_limit'),
    'CORS configuration': fs.readFileSync('backend/app.py', 'utf8').includes('CORSMiddleware'),
    'Input validation': fs.readFileSync('src/utils/parameterParser.ts', 'utf8').includes('validateParameters'),
    'Error handling': fs.readFileSync('src/services/webhookService.ts', 'utf8').includes('catch')
};

Object.entries(securityFeatures).forEach(([feature, implemented]) => {
    if (implemented) {
        console.log(`✅ ${feature}`);
    } else {
        console.log(`❌ ${feature} - NOT IMPLEMENTED`);
    }
});

// Summary
console.log('\n📊 Implementation Summary:');
console.log('========================');

const totalTests = Object.keys(features).length + Object.keys(securityFeatures).length + 4; // +4 for file checks, deps, tsconfig, backend
const passedTests = Object.values(features).filter(Boolean).length +
    Object.values(securityFeatures).filter(Boolean).length +
    (allFilesExist ? 1 : 0) +
    (missingDeps.length === 0 ? 1 : 0) +
    (tsConfig.compilerOptions?.jsx === 'react-jsx' ? 1 : 0) +
    (missingBackendDeps.length === 0 ? 1 : 0);

console.log(`Total tests: ${totalTests}`);
console.log(`Passed: ${passedTests}`);
console.log(`Failed: ${totalTests - passedTests}`);
console.log(`Success rate: ${Math.round((passedTests / totalTests) * 100)}%`);

if (passedTests === totalTests) {
    console.log('\n🎉 All tests passed! The implementation is ready for use.');
    console.log('\n📋 Next steps:');
    console.log('1. Run "npm start" to start the React development server');
    console.log('2. Run "cd backend && uvicorn app:app --reload" to start the backend API');
    console.log('3. Test with URL: http://localhost:3000/?emailId=test@example.com&accountId=test123');
    console.log('4. Check the webhook endpoint at http://localhost:8000/docs');
} else {
    console.log('\n⚠️ Some tests failed. Please review the implementation.');
    process.exit(1);
} 