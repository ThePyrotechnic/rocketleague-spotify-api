import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

git_repo = "https://github.com/thepyrotechnic/rocketleague-spotify"

setuptools.setup(
    name="rocketleague-spotify-api",
    version="0.0.0",
    author="Michael Manis, Alec Manabat",
    author_email="michaelmanis@tutanota.com",
    description="Backend API for Rocket League Spotify integration",
    license_files="LICENSE.txt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=git_repo,
    project_urls={
        "Bug Tracker": f"{git_repo}/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "python-dotenv",
        "motor"
    ],
    extras_require={
        "test": ["pytest", "requests"]
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)