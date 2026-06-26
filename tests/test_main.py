from scripts import main


def test_iter_images_returns_supported_files_in_sorted_order(dataset_root):
    cat_dir = dataset_root / "cats"
    dog_dir = dataset_root / "dogs"

    cat_png = cat_dir / "b.png"
    cat_jpg = cat_dir / "a.jpg"
    dog_webp = dog_dir / "c.webp"
    ignored = dog_dir / "notes.txt"

    for path in [cat_png, cat_jpg, dog_webp, ignored]:
        path.write_bytes(b"test")

    results = list(main.iter_images(dataset_root))

    assert results == [
        ("cats", cat_jpg),
        ("cats", cat_png),
        ("dogs", dog_webp),
    ]


def test_main_processes_each_image(monkeypatch, tmp_path):
    dataset_root = tmp_path / "dataset"
    category_dir = dataset_root / "litter"
    category_dir.mkdir(parents=True)
    image_path = category_dir / "sample.jpg"
    image_path.write_bytes(b"fake-image")

    calls = {"classified": []}

    monkeypatch.setattr(main, "DATASET_PATH", dataset_root)
    monkeypatch.setattr(main, "configure_mlflow", lambda *args, **kwargs: None)
    monkeypatch.setattr(main, "create_openai_client", lambda api_key: object())
    monkeypatch.setattr(main, "require_openai_api_key", lambda: "sk-test")
    monkeypatch.setattr(main, "classify_image_path", lambda **kwargs: calls["classified"].append(kwargs["image_path"]) or "Yes")
    monkeypatch.setattr(main, "print_summary", lambda results: calls.setdefault("summary", results))

    main.main()

    assert calls["classified"] == [image_path]
    assert calls["summary"] == [
        {
            "file": image_path,
            "category": "litter",
            "classification": "Yes",
        }
    ]
