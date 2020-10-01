module.exports = {
    branches: "master",
    repositoryUrl: "https://github.com/kawazoi/aws-ecs-worker",
    plugins: [
        '@semantic-release/commit-analyzer',
        '@semantic-release/release-notes-generator',
        ['@semantic-release/github', {
            assets: [
                { path: "coverage.zip", label: "Coverage" }
            ]
        }]
    ]
}
